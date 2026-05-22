import pandas as pd
from datetime import datetime
from sqlalchemy import text
from psycopg2.extras import execute_batch

from utils.db_sql import get_mssql_conn
from utils.db_raw import get_conn as get_pg_raw_conn
from utils.db_stg import get_conn as get_pg_stg_conn
from config.transform import transform_raw_to_stg


def get_postgres_max_val(table_name, incremental_key, room_id=None, db_type="stg"):

    conn_func = get_pg_stg_conn if db_type == "stg" else get_pg_raw_conn

    try:
        with conn_func() as conn:
            cur = conn.cursor()

            if isinstance(incremental_key, list):

                date_col, hour_col = incremental_key

                sql = f"""
                    SELECT {date_col}, {hour_col}
                    FROM {table_name}
                    WHERE {date_col} IS NOT NULL
                      AND {hour_col} IS NOT NULL
                """

                params = []
                
                # 🔥 STG 要依 room_id 查水位
                if room_id:
                    sql += " AND room_id = %s"
                    params.append(room_id)

                sql += f"""
                    ORDER BY {date_col} DESC, {hour_col} DESC
                    LIMIT 1
                """

                cur.execute(sql, params)
                row = cur.fetchone()

                return (row[0], row[1]) if row else None

    except Exception as e:
        print(f"⚠️ 無法取得水位線 (可能表尚未建立): {e}")
        return None


def run_incremental_etl(table_key, cfg, mode="stg_from_raw"):
    target_table = cfg["target_table"]
    source_table = cfg["source_table"]
    
    # 1. 決定資料庫連線與水位線檢查對象
    if mode == "raw_from_mssql":
        src_conn_func = get_mssql_conn
        target_conn_func = get_pg_raw_conn
        db_type = "raw"
        target_inc_key = cfg.get("incremental_key") 
        # 👉 RAW 直接用
        src_inc_key = cfg.get("incremental_key") 
    else:
        src_conn_func = get_pg_raw_conn
        target_conn_func = get_pg_stg_conn
        db_type = "stg"
        target_inc_key = cfg.get("incremental_key") 
        # 👉 STG 要 mapping 回 RAW
        time_map = cfg["time_mapping"]
        src_inc_key = [time_map[k] for k in target_inc_key if k in time_map]
    
    if not target_inc_key:
        raise ValueError(f"❌ {table_key} 未設定 incremental_key")

    # 2. 取得目前目標表的最大時間
    print(f"🔎 檢查 {target_table} 的水位線...")

    max_val = get_postgres_max_val(
        target_table,
        target_inc_key,
        room_id = cfg.get("room_id") if mode == "stg_from_raw" else None,
        db_type=db_type
    )

    # 3. 建構 SQL
    query = f"SELECT * FROM {source_table}"

    # 雙欄位
    if isinstance(target_inc_key, list):

        date_key, hour_key = src_inc_key

        if not max_val:

            print(f"🚀 目標表目前為空，開始全量初始化...")

            query += f"""
            ORDER BY
                CAST({date_key} AS DATE),
                CAST({hour_key} AS INTEGER)
            """

        else:

            last_date, last_hour = max_val

            print(
                f"📈 偵測到上次同步至: "
                f"{last_date} {last_hour}:00，執行增量抓取..."
            )

            # MSSQL / PostgreSQL 今天日期語法
            today_sql = (
                "CAST(GETDATE() AS DATE)"
                if mode == "raw_from_mssql"
                else "CURRENT_DATE"
            )

            query += f"""
            WHERE
            (
                CAST({date_key} AS DATE) = '{last_date}'
                AND CAST({hour_key} AS INTEGER) > {int(last_hour)}
            )

            OR

            (
                CAST({date_key} AS DATE) > '{last_date}'
            )

            ORDER BY
                CAST({date_key} AS DATE),
                CAST({hour_key} AS INTEGER)
            """

    else:
        raise ValueError("❌ {table_key} 未設定 incremental_key")

    # 4. 執行同步
    with src_conn_func() as src_conn:
        print(f"📡 執行 SQL 查詢來源表: {query}")
        reader = pd.read_sql(query, src_conn, chunksize=500000)
        
        total_count = 0
        for i, chunk in enumerate(reader):
            if chunk.empty:
                continue

            df = chunk

            # =========================
            # 🔹 STG transform（only STG）
            # =========================
            if mode == "stg_from_raw":
                df = transform_raw_to_stg(df, cfg)
                print(f"🔧 欄位轉換: {len(chunk)} → {len(df)}")

            # 補充審核欄位
            now = datetime.now()
            df["created_at"] = now
            df["updated_at"] = now

            records = df.to_dict("records")
            # print("RAW cols:", df.columns.tolist())
            # print("METRIC keys:", list(cfg["metric_mapping"].keys()))

            # 寫入目標
            with target_conn_func() as pg_conn:
                with pg_conn.cursor() as cur:

                    cols = df.columns.tolist()

                    sql = f"""
                        INSERT INTO {target_table}
                        ({', '.join(cols)})
                        VALUES ({', '.join([f'%({c})s' for c in cols])})
                        ON CONFLICT DO NOTHING;
                    """

                    execute_batch(cur, sql, records)

                    # print("SOURCE TABLE CHECK:")
                    # print(df.head(3))
                    # print(df.columns.tolist())

                    total_count += len(df)
                    print(f"➕ [{db_type.upper()}] 寫入第 {i+1} 批次完成，累計 {total_count} 筆")

                pg_conn.commit()

    print(f"🎉 {table_key} 同步程序結束，共計處理 {total_count} 筆資料。")