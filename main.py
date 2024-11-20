import requests
import mysql.connector
from config import db_config, tmdb_auth

# Connect to MySQL database
try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    print("Connected to MySQL database")
except mysql.connector.Error as err:
    print(f"Error: {err}")
    exit()

# Create a table to store movie data if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS top_movies (
    id INT PRIMARY KEY,
    title VARCHAR(255),
    release_date DATE,
    revenue BIGINT,
    vote_average FLOAT,
    vote_count INT,
    overview TEXT
);
''')

page = 1

# API call to retrieve the top movies
base_url = "https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&primary_release_year=2023&sort_by=revenue.desc&page="

headers = {
    "accept": "application/json",
    "Authorization": f"{tmdb_auth}"
}

movies_collected = 0
movies_data = []

while movies_collected < 250:
    response = requests.get(base_url + str(page), headers=headers)
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        break

    results = response.json().get('results', [])

    if not results:
        print("No more results found.")
        break

    for movie in results:
        # Check if we've already collected 250 movies
        if movies_collected >= 250:
            break

        # Prepare movie data for insertion
        movie_data = (
            movie['id'],
            movie['title'],
            movie['release_date'],
            movie.get('revenue', 0),
            movie['vote_average'],
            movie['vote_count'],
            movie['overview']
        )
        movies_data.append(movie_data)
        movies_collected += 1

    page += 1

# Insert data into the database
insert_query = '''
INSERT INTO top_movies (id, title, release_date, revenue, vote_average, vote_count, overview)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
title=VALUES(title), release_date=VALUES(release_date), revenue=VALUES(revenue),
vote_average=VALUES(vote_average), vote_count=VALUES(vote_count), overview=VALUES(overview);
'''

if movies_data:
    cursor.executemany(insert_query, movies_data)
    conn.commit()
    print(f"{len(movies_data)} movies inserted into the database.")
else:
    print("No movie data was collected.")

# Close the database connection
cursor.close()
conn.close()
