from utils.db_stg import get_conn

TABLE_NAME = "public.sensor_room_energy_hourly"
TABLE_COMMENT = "教室每小時用電量原始資料（統一指標）"

COLUMNS = [
    ("id", "BIGSERIAL PRIMARY KEY", True, "資料識別碼"),

    ("room_id", "VARCHAR(10)", True, "教室編號"),

    ("energy_date", "DATE", True, "用電日期"),
    ("energy_hour", "SMALLINT", True, "用電小時"),

    ("metric_type", "VARCHAR(50)", True, "用電類型（electric/air/light）"),
    ("metric_name", "VARCHAR(50)", True, "用電細項（AC_A/LIGHT_1/TOTAL 等）"),
    ("metric_value", "NUMERIC(12,4)", False, "用電數值"),

    ("created_at", "TIMESTAMP(6)", True, "建立時間"),
    ("updated_at", "TIMESTAMP(6)", True, "更新時間"),
]

# 唯一鍵，避免同一電表重複
UNIQUE_KEYS = ["room_id", "energy_date", "energy_hour", "metric_type", "metric_name"]

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
