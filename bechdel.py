import requests
import mysql.connector
from config import db_config


# Function to get movie information from Bechdel Test API by IMDb ID
def get_movie_info(imdb):
    url = f"http://bechdeltest.com/api/v1/getMovieByImdbId?imdbid={imdb}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return {
            "id": data.get("id"),
            "rating": data.get("rating"),
            "dubious": data.get("dubious"),
        }
    else:
        print(f"Failed to get data for IMDb ID {imdb}: {response.status_code}")
        return None


# Database connection setup
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Create the `rating` table if it does not exist, using the `id` from `top_movies` as the primary key
create_table_query = """
CREATE TABLE IF NOT EXISTS rating (
    id INT PRIMARY KEY,
    rating INT,
    dubious TINYINT
)
"""
cursor.execute(create_table_query)
print("Table `rating` checked/created successfully.")

# Query to get all IMDb IDs and original IDs from the `ids` table
cursor.execute("SELECT id, imdb_id FROM ids")
movies = cursor.fetchall()

# Iterate over each movie and get film info from the Bechdel Test API
for movie in movies:
    original_id, imdb_id = movie
    movie_info = get_movie_info(imdb_id)

    if movie_info and movie_info["rating"] is not None:
        # Insert the original ID (from `top_movies`), rating, and dubious field into the `rating` table
        insert_query = "INSERT INTO rating (id, rating, dubious) VALUES (%s, %s, %s)"
        try:
            cursor.execute(insert_query, (original_id, movie_info["rating"], movie_info["dubious"]))
            print(
                f"Inserted movie info for original ID {original_id} with rating {movie_info['rating']} and dubious {movie_info['dubious']}")
        except mysql.connector.IntegrityError:
            print(f"Original ID {original_id} already exists in the `rating` table. Skipping insertion.")
    else:
        print(f"Could not insert movie info for original ID {original_id} due to missing data")

# Commit changes and close the connection
conn.commit()
cursor.close()
conn.close()

print("Movie info insertion process completed.")
