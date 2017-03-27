import boto3
# http://mysqlclient.readthedocs.io/en/latest/user_guide.html#mysqldb
import MySQLdb

print("started")

DB_HOST = "mysql"

db = MySQLdb.connect(host=DB_HOST, db="mysql")

# TODO fetch error log

with db as cursor:
    cursor.execute("SET GLOBAL log_output = 'TABLE'")
    cursor.execute("SET GLOBAL general_log = 'ON'")
    db.commit()

with db as cursor:
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    for (table_name,) in tables:
        print(table_name)

with db as cursor:
    # TODO select since last time
    cursor.execute("SELECT * FROM general_log")
    for row in cursor:
        print(row)
