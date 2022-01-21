import psycopg2

conn = psycopg2.connect(
   database="db_cities_regions", user='postgres', password='postgres', host='localhost', port='5432'
)


cursor = conn.cursor()
sql = """SELECT * FROM regions"""
cursor.execute(sql)
result = cursor.fetchall()
print(result)

conn.close()
