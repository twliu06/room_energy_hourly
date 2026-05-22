import warnings
from config.config import RAW_CONFIG
from utils.incremental import run_incremental_etl

# =========================
# 🚫 關掉 pandas warning
# =========================
warnings.filterwarnings(
    "ignore",
    message="pandas only supports SQLAlchemy"
)

def main():
    print(f"🚀 將跑所有表，共 {len(RAW_CONFIG)} 張")

    for table_key, cfg in RAW_CONFIG.items():
        print(f"\n⚡ 開始處理: {table_key}")
        run_incremental_etl(table_key, cfg, mode="raw_from_mssql")

    print(f"🎉 所有表增量同步完成")


if __name__ == "__main__":
    main()