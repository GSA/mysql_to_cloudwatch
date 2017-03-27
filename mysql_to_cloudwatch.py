import boto3
import MySQLdb

print("started")

db = MySQLdb.connect(host="mysql", db="mysql")
c = db.cursor()

c.execute("SHOW TABLES")
tables = c.fetchall()
for (table_name,) in tables:
    print(table_name)
