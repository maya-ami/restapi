import psycopg2

conn = psycopg2.connect(
   database="postgres", user='postgres', password='postgres', host='localhost', port='5432'
)
conn.autocommit = True


cursor = conn.cursor()
sql = """SELECT * FROM cities"""
cursor.execute(sql)
result = cursor.fetchall()
print(result)

conn.close()
