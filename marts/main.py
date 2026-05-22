import warnings
from config.config import RAW_CONFIG, STG_CONFIG
from utils.incremental import run_incremental_etl

# =========================
# 🚫 關掉 pandas warning
# =========================
warnings.filterwarnings(
    "ignore",
    message="pandas only supports SQLAlchemy"
)

def main():
    # =========================
    # 🔹 STEP 1: RAW LOAD
    # =========================
    print("\n===== RAW LOAD =====")

    for table_key, cfg in RAW_CONFIG.items():
        print(f"\n⚡ 開始處理 RAW 表: {table_key}")
        run_incremental_etl(
            table_key=table_key,
            cfg=cfg,
            mode="raw_from_mssql"
        )
    
    # =========================
    # 🔹 STEP 2: STG LOAD
    # =========================
    print("\n===== STG LOAD =====")
    
    for table_key, cfg in STG_CONFIG.items():
        print(f"\n⚡ 開始處理 STG 表: {table_key}")

        run_incremental_etl(
            table_key=table_key,
            cfg=cfg,
            mode="stg_from_raw"
        )
    
    print(f"🎉 所有表增量同步完成")


if __name__ == "__main__":
    main()