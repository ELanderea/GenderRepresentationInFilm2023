import requests
import mysql.connector
from config import db_config, tmdb_auth

# Database connection setup
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Create the `ids` table if it does not exist
create_table_query = """
CREATE TABLE IF NOT EXISTS ids (
    id INT PRIMARY KEY,
    imdb_id VARCHAR(15)
)
"""
cursor.execute(create_table_query)
print("Table `ids` checked/created successfully.")


# Function to get IMDb ID for a given TMDB movie ID
def get_imdb_id(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?language=en-US"
    headers = {
        "accept": "application/json",
        "Authorization": f"{tmdb_auth}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get("imdb_id")
    else:
        print(f"Failed to get data for movie ID {tmdb_id}: {response.status_code}")
        return None


# Query to get all movie IDs from the `top_movies` table
cursor.execute("SELECT id FROM top_movies")
movies = cursor.fetchall()

# Iterate over each movie ID, get the IMDb ID, and insert both into the `ids` table
for movie in movies:
    tmdb_movie_id = movie[0]  # Extract the movie ID from the tuple
    imdb_id = get_imdb_id(tmdb_movie_id)

    if imdb_id:
        # Insert the original ID and IMDb ID into the `ids` table
        insert_query = "INSERT INTO ids (id, imdb_id) VALUES (%s, %s)"
        try:
            cursor.execute(insert_query, (tmdb_movie_id, imdb_id))
            print(f"Inserted movie ID {tmdb_movie_id} with IMDb ID {imdb_id}")
        except mysql.connector.IntegrityError:
            print(f"Movie ID {tmdb_movie_id} already exists in the `ids` table. Skipping insertion.")
    else:
        print(f"Could not obtain IMDb ID for movie ID {tmdb_movie_id}")

# Commit changes and close the connection
conn.commit()
cursor.close()
conn.close()

print("IMDb ID insertion process completed.")
