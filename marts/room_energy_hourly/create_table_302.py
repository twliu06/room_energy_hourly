from utils.db_raw import get_conn

TABLE_NAME = "sensor.room_302_energy_hourly"
TABLE_COMMENT = "土302 教室每小時用電量資料（來源：SQL Server View_KWH_hr_302）"

# (欄位名稱, 型別, NOT NULL, 欄位註解)
COLUMNS = [
    ("id", "BIGSERIAL PRIMARY KEY", True, "資料識別碼"),

    ("Date_Civil_E302", "TEXT", False, "日期欄位 (原始)"),
    ("DATE_E302_H", "SMALLINT", False, "小時欄位 (原始)"),

    ("PC_L1", "TEXT", False, "插座用電L1 (原始)"),
    ("PC_L2", "TEXT", False, "插座用電L2 (原始)"),
    ("PC_Total", "TEXT", False, "插座總用電 (原始)"),

    ("Light1", "TEXT", False, "照明1 (原始)"),
    ("Light4", "TEXT", False, "照明4 (原始)"),
    ("Light2", "TEXT", False, "照明2 (原始)"),
    ("Light3", "TEXT", False, "照明3 (原始)"),
    ("Light5", "TEXT", False, "照明5 (原始)"),

    ("ACA", "TEXT", False, "空調A (原始)"),
    ("ACb", "TEXT", False, "空調B (原始)"),
    ("ACC", "TEXT", False, "空調C (原始)"),
    ("ACD", "TEXT", False, "空調D (原始)"),

    ("created_at", "TIMESTAMP(6)", True, "資料建立時間"),
    ("updated_at", "TIMESTAMP(6)", True, "資料更新時間"),
]

UNIQUE_KEYS = ["Date_Civil_E302", "DATE_E302_H"]

def build_create_table_sql() -> str:
    col_defs = []

    for name, dtype, not_null, _ in COLUMNS:
        nn = " NOT NULL" if not_null and "PRIMARY KEY" not in dtype else ""
        col_defs.append(f"    {name} {dtype}{nn}")

    col_defs.append(f"    UNIQUE ({', '.join(UNIQUE_KEYS)})")
    
    return f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
{",\n".join(col_defs)}
);
"""

def build_comment_sql() -> list[str]:
    stmts = [
        f"COMMENT ON TABLE {TABLE_NAME} IS '{TABLE_COMMENT}';"
    ]

    for name, _, _, comment in COLUMNS:
        if comment:
            stmts.append(
                f"COMMENT ON COLUMN {TABLE_NAME}.{name} IS '{comment}';"
            )

    return stmts

def main():
    with get_conn(autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(build_create_table_sql())

            for stmt in build_comment_sql():
                cur.execute(stmt)

            print(f"✅ {TABLE_NAME} 建表完成")

if __name__ == "__main__":
    main()
