import psycopg2
from app import db
from werkzeug.security import generate_password_hash

# estblish the connection
conn = psycopg2.connect(
   database='postgres', user='postgres', password='postgres', host='localhost', port='5432'
)
conn.autocommit = True
cursor = conn.cursor()


# create a new db
sql = """CREATE database db_cities_regions""";
cursor.execute(sql)
print("Database created successfully.")
conn.commit()
conn.close()

# create new tables
db.create_all()

# connect to the new db
conn = psycopg2.connect(
   database='db_cities_regions', user='postgres', password='postgres', host='localhost', port='5432'
)
cursor = conn.cursor()

# encrypt passwords for users
hash_1 = generate_password_hash('password_for_example')
hash_2 = generate_password_hash('one_more_sample_password')

# insert data to the tables
users_vals = """INSERT INTO users(id, username, password) VALUES (1,'user_1', '{}');
                INSERT INTO users(id, username, password) VALUES (2,'user_2', '{}');""".format(hash_1, hash_2)

regions_vals = """INSERT INTO regions(id, name) VALUES (1, 'Bashkortostan Republic');
                INSERT INTO regions(id, name) VALUES (2, 'Tatarstan Republic');
                INSERT INTO regions(id, name) VALUES (3, 'Murmanskaya oblast');
                INSERT INTO regions(id, name) VALUES (4, 'Sverdlovskaya oblast');"""

cities_vals = """INSERT INTO cities(id, region_id, name) VALUES (1, 1, 'Ufa');
                INSERT INTO cities(id, region_id, name) VALUES (2, 1, 'Sterlitamak');
                INSERT INTO cities(id, region_id, name) VALUES (3, 1, 'Kumertau');
                INSERT INTO cities(id, region_id, name) VALUES (4, 2, 'Kazan');
                INSERT INTO cities(id, region_id, name) VALUES (5, 2, 'Innopolis');
                INSERT INTO cities(id, region_id, name) VALUES (6, 3, 'Murmansk');
                INSERT INTO cities(id, region_id, name) VALUES (7, 3, 'Teriberka');
                INSERT INTO cities(id, region_id, name) VALUES (8, 4, 'Ekaterinburg');
                INSERT INTO cities(id, region_id, name) VALUES (9, 4, 'Pervouralsk');"""

cursor.execute(users_vals)
cursor.execute(regions_vals)
cursor.execute(cities_vals)

conn.commit()
conn.close()
