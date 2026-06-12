import os
import warnings
from utils.logger import get_logger
from config.config import RAW_CONFIG, STG_CONFIG
from utils.incremental import run_incremental_etl

# =========================
# 🚫 關掉 pandas warning
# =========================
warnings.filterwarnings(
    "ignore",
    message="pandas only supports SQLAlchemy"
)

BASE_DIR = os.path.dirname(__file__)
LOG_DIR = os.path.join(BASE_DIR, "logs")

print_log = get_logger(
    log_dir=LOG_DIR,
    log_prefix="room_energy_hourly"
)

def main():
    # =========================
    # 🔹 STEP 1: RAW LOAD
    # =========================
    print_log("\n===== RAW LOAD =====")

    for table_key, cfg in RAW_CONFIG.items():
        print_log(f"\n⚡ 開始處理 RAW 表: {table_key}")
        run_incremental_etl(
            table_key=table_key,
            cfg=cfg,
            mode="raw_from_mssql"
        )
    
    # =========================
    # 🔹 STEP 2: STG LOAD
    # =========================
    print_log("\n===== STG LOAD =====")
    
    for table_key, cfg in STG_CONFIG.items():
        print_log(f"\n⚡ 開始處理 STG 表: {table_key}")

        run_incremental_etl(
            table_key=table_key,
            cfg=cfg,
            mode="stg_from_raw"
        )
    
    print_log(f"🎉 所有表增量同步完成")


if __name__ == "__main__":
    main()