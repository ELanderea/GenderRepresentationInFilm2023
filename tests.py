import requests
import mysql.connector
from config import tmdb_auth, db_config
import html


# Function to get movie title from TMDB by TMDB movie ID
def get_tmdb_title(tmdb_movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{tmdb_movie_id}?language=en-US"
        headers = {
            "accept": "application/json",
            "Authorization": f"{tmdb_auth}"
        }
        response = requests.get(url, headers=headers)

        response.raise_for_status()  # Raise an HTTPError for bad responses

        data = response.json()
        return data.get("title")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred for TMDB ID {tmdb_movie_id}: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred for TMDB ID {tmdb_movie_id}: {req_err}")
    except Exception as err:
        print(f"An unexpected error occurred for TMDB ID {tmdb_movie_id}: {err}")
    return None


# Function to get movie title from Bechdel Test API by IMDb ID
def get_bechdel_title(imdb_id):
    try:
        url = f"http://bechdeltest.com/api/v1/getMovieByImdbId?imdbid={imdb_id}"
        response = requests.get(url)

        response.raise_for_status()  # Raise an HTTPError for bad responses

        data = response.json()
        return data.get("title")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred for IMDb ID {imdb_id}: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred for IMDb ID {imdb_id}: {req_err}")
    except Exception as err:
        print(f"An unexpected error occurred for IMDb ID {imdb_id}: {err}")
    return None


# Function to format film titles, e.g., 'Matrix, The' -> 'The Matrix'
def fix_film_title(title):
    title = html.unescape(title)  # Decode HTML entities (e.g., '&#39;' to "'")
    words = ["The", "A", "An"]
    sections = title.rsplit(',', 1)  # Split the title at the last comma
    if len(sections) == 2:
        section_1 = sections[0].strip()
        section_2 = sections[1].strip()
        if section_2 in words:
            return f'{section_2} {section_1}'
    return title


# Database connection setup
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Query to get all TMDB IDs and IMDb IDs from the `ids` table
cursor.execute("SELECT id, imdb_id FROM ids")
movies = [{"tmdb_id": row[0], "imdb_id": row[1][2:] if row[1].startswith("tt") else row[1]} for row in
          cursor.fetchall()]

# Close the database connection after retrieving data
cursor.close()
conn.close()

# Iterate over each movie and compare titles
for movie in movies:
    tmdb_id = movie["tmdb_id"]
    imdb_id = movie["imdb_id"]

    # Get TMDB title with error handling
    tmdb_title = get_tmdb_title(tmdb_id)
    if tmdb_title is None:
        print(f"Skipping comparison for TMDB ID {tmdb_id} due to error in retrieving TMDB title.")
        continue

    # Get Bechdel title with error handling
    bechdel_title = get_bechdel_title(imdb_id)
    if bechdel_title is None:
        print(f"Skipping comparison for IMDb ID {imdb_id} due to error in retrieving Bechdel title.")
        continue
    if tmdb_title and bechdel_title:
        # Apply formatting to the Bechdel title
        formatted_bechdel_title = fix_film_title(bechdel_title)

        if tmdb_title.lower() == formatted_bechdel_title.lower():
            print(f"Titles match for TMDB ID {tmdb_id} and IMDb ID {imdb_id}: '{tmdb_title}'")
        else:
            print(f"Titles do NOT match for TMDB ID {tmdb_id} and IMDb ID {imdb_id}:")
            print(f" - TMDB Title: '{tmdb_title}'")
            print(f" - Bechdel Title: '{formatted_bechdel_title}'")
    else:
        print(f"Could not retrieve titles for TMDB ID {tmdb_id} or IMDb ID {imdb_id}")

print("Title comparison process completed.")
