import pyodbc

# def get_mssql_conn():
#     conn = pyodbc.connect(
#         "DRIVER={ODBC Driver 17 for SQL Server};"
#         "SERVER=140.134.5.93,1433;"
#         "DATABASE=FCU_Computer2;"
#         "UID=onlyview1;"
#         "PWD=Dispute-Fid-1;"
#         "TrustServerCertificate=yes;"
#     )

#     return conn


def get_mssql_conn():
    conn = pyodbc.connect(
	'DRIVER={FreeTDS};'
        'SERVER=140.134.5.93;'
	'PORT=1433;'
        'DATABASE=FCU_Computer2;'
        'UID=onlyview1;'
        'PWD=Dispute-Fid-1;'
	'TDS_Version=7.3;'
        'client_charset=UTF-8;'
    )

    return conn