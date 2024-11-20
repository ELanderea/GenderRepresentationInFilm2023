import requests
from config import db_config, tmdb_auth
import mysql.connector

# Connect to MySQL database
try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    print("Connected to MySQL database")
except mysql.connector.Error as err:
    print(f"Error: {err}")
    exit()

# Create the 'directors' table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS directors (
    movie_id INT PRIMARY KEY,
    director_name VARCHAR(255),
    job VARCHAR(255),
    gender INT,
    FOREIGN KEY (movie_id) REFERENCES top_movies(id)
);
''')

# Fetch movie IDs from the database
cursor.execute("SELECT id FROM top_movies")
movie_ids = [movie_id[0] for movie_id in cursor.fetchall()]


# API base URL for movie credits
base_url = "https://api.themoviedb.org/3/movie/{}/credits?language=en-US"

headers = {
    "accept": "application/json",
    "Authorization": f"{tmdb_auth}"
}
# Counter for the number of directors found
director_count = 0

# Iterate through each movie ID and fetch crew information
for movie_id in movie_ids:
    response = requests.get(base_url.format(movie_id), headers=headers)

    if response.status_code == 200:
        dir_credits = response.json().get('crew', [])
        for crew_member in dir_credits:
            if crew_member['job'] == 'Director':
                director_count += 1
                # Insert director data into the 'directors' table
                insert_query = '''
                INSERT INTO directors (movie_id, director_name, job, gender)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                director_name=VALUES(director_name), job=VALUES(job), gender=VALUES(gender);
                '''
                cursor.execute(insert_query, (
                    movie_id,
                    crew_member['name'],
                    crew_member['job'],
                    crew_member.get('gender', 0)  # Gender can be 0 (unknown), 1 (female), or 2 (male)
                ))
                conn.commit()
    else:
        print(f"Failed to fetch crew data for movie ID {movie_id}. Status code: {response.status_code}")

# Print the total number of directors found
print(f"Total number of directors found: {director_count}")

# Close the database connection
cursor.close()
conn.close()
