import pandas as pd

def transform_raw_to_stg(df, cfg):

    # DataFrame 欄位統一小寫
    df.columns = df.columns.str.lower()

    # Config 欄位也統一小寫
    time_mapping = {
        k: v.lower()
        for k, v in cfg["time_mapping"].items()
    }

    metric_mapping = {
        k.lower(): v
        for k, v in cfg["metric_mapping"].items()
    }

    room_id = cfg["room_id"]

    results = []

    date_col = time_mapping["energy_date"]
    hour_col = time_mapping["energy_hour"]

    for _, row in df.iterrows():

        energy_date = pd.to_datetime(row[date_col]).date()
        energy_hour = int(row[hour_col])

        for raw_col, (metric_type, metric_name) in metric_mapping.items():

            value = row.get(raw_col)

            if value is None or value == "" or pd.isna(value):
                continue

            results.append({
                "room_id": room_id,
                "energy_date": energy_date,
                "energy_hour": energy_hour,
                "metric_type": metric_type,
                "metric_name": metric_name,
                "metric_value": float(value),
            })

    return pd.DataFrame(results)