import pyodbc


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


#import pytds

#def get_mssql_conn():
#    conn = pytds.connect(
#	server='140.134.5.93',
#	port=1433,
#	user='onlyview1',
#	password='Dispute-Fid-1',
#	database='FCU_Computer2',
#	autocommit=True,
#	encryption_level=0
#   )
#    return conn
