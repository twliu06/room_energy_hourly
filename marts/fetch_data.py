import pandas as pd
import warnings
warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")


def fetch_view_data(conn, view_name, chunk_size=50000):
    """
    從 SQL Server View 抓資料（chunk 方式）

    Args:
        conn: pyodbc connection
        view_name (str): View 名稱（例如 View_KWH_hr_302）
        chunk_size (int): 每次抓取筆數
        schema (str): schema 名稱（預設 dbo）

    Yields:
        pd.DataFrame: 原始資料（未做任何轉換）
    """

    query = f"SELECT * FROM {view_name}"

    for chunk in pd.read_sql(query, conn, chunksize=chunk_size):
        yield chunk


def fetch_multiple_views(conn, view_configs, chunk_size=50000):
    """
    同時處理多個 View

    Args:
        conn: pyodbc connection
        view_configs (list): [(view_name, room_id), ...]
        chunk_size (int): 每次抓取筆數
        schema (str): schema 名稱

    Yields:
        tuple: (view_name, room_id, chunk)
    """

    for view_name, room_id in view_configs:
        print(f"🚀 開始抓取 {view_name}")

        for chunk in fetch_view_data(conn, view_name, chunk_size):
            yield view_name, room_id, chunk

        print(f"✅ 完成 {view_name}")