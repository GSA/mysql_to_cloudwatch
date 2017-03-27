import boto3
import MySQLdb

print("started")

db = MySQLdb.connect(host="mysql", db="mysql")
c = db.cursor()

# TODO fetch error log

c.execute("SET GLOBAL log_output = 'TABLE'")
c.execute("SET GLOBAL general_log = 'ON'")
db.commit()

c.execute("SHOW TABLES")
tables = c.fetchall()
for (table_name,) in tables:
    print(table_name)

# TODO select since last time
c.execute("SELECT * FROM general_log")
rows = c.fetchall()
for row in rows:
    print(row)
