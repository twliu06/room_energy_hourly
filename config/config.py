RAW_CONFIG = {
    "room_302": {
        "source_table": "dbo.View_KWH_hr_302",
        "target_table": "sensor.room_302_energy_hourly",
        "incremental_key": ["Date_Civil_E302", "DATE_E302_H"],
    },
    "room_504": {
        "source_table": "dbo.View_KWH_hr_504",
        "target_table": "sensor.room_504_energy_hourly",
        "incremental_key": ["DATE_504", "DATE_504_H"],
    },
    "room_611": {
        "source_table": "dbo.View_KWH_hr_611",
        "target_table": "sensor.room_611_energy_hourly",
        "incremental_key": ["DATE_611", "DATE_611_H"],
    },
}

STG_CONFIG = {
    "room_302": {
        "room_id": "302",
        "source_table": "sensor.room_302_energy_hourly",
        "target_table": "public.sensor_room_energy_hourly",
        "incremental_key": ["energy_date", "energy_hour"],
        "time_mapping": {
            "energy_date": "Date_Civil_E302",
            "energy_hour": "DATE_E302_H"
        },
        "metric_mapping": {
            "PC_L1": ("equipment", "power_l1_kwh"),
            "PC_L2": ("equipment", "power_l2_kwh"),
            "PC_Total": ("equipment", "power_total_kwh"),
            "Light1": ("lighting", "lighting_zone_1_kwh"),
            "Light2": ("lighting", "lighting_zone_2_kwh"),
            "Light3": ("lighting", "lighting_zone_3_kwh"),
            "Light4": ("lighting", "lighting_zone_4_kwh"),
            "Light5": ("lighting", "lighting_zone_5_kwh"),
            "ACA": ("air", "air_conditioner_a_kwh"),
            "ACB": ("air", "air_conditioner_b_kwh"),
            "ACC": ("air", "air_conditioner_c_kwh"),
            "ACD": ("air", "air_conditioner_d_kwh"),
        },
    },
    "room_504": {
        "room_id": "504",
        "source_table": "sensor.room_504_energy_hourly",
        "target_table": "public.sensor_room_energy_hourly",
        "incremental_key": ["energy_date", "energy_hour"],
        "time_mapping": {
            "energy_date": "DATE_504",
            "energy_hour": "DATE_504_H"
        },
        "metric_mapping": {
            "Elc_IP_KWH_Hr": ("electric", "power_total_kwh"),
            "Air_A_KWH_Hr": ("air", "air_conditioner_a_kwh"),
            "Air_B_KWH_Hr": ("air", "air_conditioner_b_kwh"),
            "Air_C_KWH_Hr": ("air", "air_conditioner_c_kwh"),
        },
    },
    "room_611": {
        "room_id": "611",
        "source_table": "sensor.room_611_energy_hourly",
        "target_table": "public.sensor_room_energy_hourly",
        "incremental_key": ["energy_date", "energy_hour"],
        "time_mapping": {
            "energy_date": "DATE_611",
            "energy_hour": "DATE_611_H"
        },
        "metric_mapping": {
            "Elc_IP_KWH_Day": ("electric", "power_total_kwh"),
            "Air_A_KWH_Day": ("air", "air_conditioner_a_kwh"),
            "Air_B_KWH_Day": ("air", "air_conditioner_b_kwh"),
            "Air_C_KWH_Day": ("air", "air_conditioner_c_kwh"),
            "Air_D_KWH_Day": ("air", "air_conditioner_d_kwh"),
            "Air_E_KWH_Day": ("air", "air_conditioner_e_kwh"),
        },
    },
}