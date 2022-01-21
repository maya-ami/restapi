import psycopg2

conn = psycopg2.connect(
   database="regions", user='postgres', password='postgres', host='localhost', port='5432'
)


cursor = conn.cursor()
sql = """SELECT cities.name FROM cities WHERE cities.region_id = 1"""
cursor.execute(sql)
result = cursor.fetchall()
print(result)

conn.close()
