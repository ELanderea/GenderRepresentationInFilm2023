import mysql.connector
from config import db_config

# Database connection setup
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Update query to remove the "tt" prefix from the imdb_id column if it exists
clean_query = """
UPDATE ids
SET imdb_id = SUBSTRING(imdb_id, 3)
WHERE imdb_id LIKE 'tt%';
"""

# Execute the query
cursor.execute(clean_query)
print("IMDb IDs cleaned by removing the 'tt' prefix if it existed.")

# Commit changes and close the connection
conn.commit()
cursor.close()
conn.close()

print("Database update process completed.")
