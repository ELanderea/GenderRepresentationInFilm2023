import pandas as pd
from sqlalchemy import create_engine
from config import db_config
import matplotlib.pyplot as plt

# Create a database connection string using SQLAlchemy
connection_string = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
engine = create_engine(connection_string)

# Load the Bechdel score, director, and composer gender data
query = """
SELECT t.id, t.vote_average, r.rating AS bechdel_score, 
       d.director_name, d.job AS director_job, d.gender AS director_gender, 
       c.composer_name, c.job AS composer_job, c.gender AS composer_gender
FROM top_movies t
JOIN rating r ON t.id = r.id
LEFT JOIN directors d ON t.id = d.movie_id
LEFT JOIN composers c ON t.id = c.movie_id
"""
df = pd.read_sql(query, engine)
engine.dispose()

# Overall Average Bechdel Score
average_bechdel_score = df['bechdel_score'].mean()
print("Average Bechdel Score:", average_bechdel_score)

# Average Bechdel score by Director gender
male_director_avg_bechdel = df[df['director_gender'] == 2]['bechdel_score'].mean()
female_director_avg_bechdel = df[df['director_gender'] == 1]['bechdel_score'].mean()
print("Average Bechdel Score for Films with Male Directors:", male_director_avg_bechdel)
print("Average Bechdel Score for Films with Female Directors:", female_director_avg_bechdel)

categories = ['Overall', 'Male Directors', 'Female Directors']
scores = [average_bechdel_score, male_director_avg_bechdel, female_director_avg_bechdel]

plt.figure(figsize=(10, 6))
plt.bar(categories, scores, color=['#7b6603', '#5e25be', '#07600d', '#a7a3a8'])
plt.title('Average Bechdel Score Comparison for Top 250 Films of 2023')
plt.xlabel('Category', labelpad=10, fontweight='bold')
plt.ylabel('Average\nBechdel\nScore', labelpad=5, fontweight='bold', rotation=0)
plt.gca().yaxis.set_label_coords(-0.1, 0.5)  # Move the label to specific coordinates (x, y)
plt.ylim(0, 3)  # Bechdel scores range from 0 to 3
plt.xticks(rotation=0)
plt.show()

# Composer Gender Distribution
composer_gender_distribution = df['composer_gender'].value_counts(normalize=True) * 100
print("Composer Gender Distribution:\n", composer_gender_distribution)

# Director Gender Distribution
director_gender_distribution = df['director_gender'].value_counts(normalize=True) * 100
print("Director Gender Distribution:\n", director_gender_distribution)

# Composer Gender when Directors = Female
female_director_composer_breakdown = df[df['director_gender'] == 1]['composer_gender'].value_counts(
    normalize=True) * 100
print("Composer Gender Breakdown When Directors are Female:\n", female_director_composer_breakdown)

# Composer Gender when Directors = Male
male_director_composer_breakdown = df[df['director_gender'] == 2]['composer_gender'].value_counts(normalize=True) * 100
print("Composer Gender Breakdown When Directors are Male:\n", male_director_composer_breakdown)

# Breakdown of Average Vote Score by Director gender
male_director_avg_vote = df[df['director_gender'] == 2]['vote_average'].mean()
female_director_avg_vote = df[df['director_gender'] == 1]['vote_average'].mean()
print("Average TMDB Scores for Films with Male Directors:", male_director_avg_vote)
print("Average TMDB Scores for Films with Female Directors:", female_director_avg_vote)

categories_vote = ['Male Directors', 'Female Directors']
vote_averages = [male_director_avg_vote, female_director_avg_vote]

# Visualisation: Gender Distribution of Composers
# Explode specific slices to separate them slightly
explode = [0.1 if p < 15 else 0 for p in composer_gender_distribution]  # Explode small slices (< 15%)


def format_autopct(pct):
    """Format percentages with one decimal place and add them outside the pie chart."""
    return f'{pct:.1f}%'


plt.figure(figsize=(10, 6))
composer_gender_distribution.plot(
    kind='pie',
    colors=['#5e25be', '#7b6603', '#07600d', '#a7a3a8'],
    labels=None,
    startangle=90,
    autopct=format_autopct,
    pctdistance=1.1,
    explode=explode
)

plt.legend(
    labels=['Male', 'Unknown', 'Female', 'Non-binary'],
    title='Composer Gender',
    loc='upper right',
    bbox_to_anchor=(1.25, 0.9)
)

plt.title('Gender Distribution of Composers for Top 250 Films of 2023', pad=20)
plt.ylabel('')
plt.show()

# Visualisation: Gender Distribution of Directors
# Explode specific slices to separate them slightly
explode = [0.1 if p < 15 else 0 for p in director_gender_distribution]  # Explode small slices (< 15%)

plt.figure(figsize=(10, 6))
director_gender_distribution.plot(
    kind='pie',
    colors=['#5e25be', '#07600d', '#7b6603', '#a7a3a8'],
    labels=None,
    startangle=90,
    autopct=format_autopct,
    pctdistance=1.1,
    explode=explode
)

plt.legend(
    labels=['Male', 'Female', 'Unknown', 'Non-binary'],
    title='Director Gender',
    loc='upper right',
    bbox_to_anchor=(1.25, 0.9)
)

plt.title('Gender Distribution of Directors for Top 250 Films of 2023', pad=20)
plt.ylabel('')
plt.show()

# Visualisation: Composer Gender when Directors = Female
plt.figure(figsize=(10, 6))
female_director_composer_breakdown.plot(kind='bar', color=['#5e25be', '#7b6603', '#07600d', '#a7a3a8'])
plt.title('Composer Gender Breakdown for Top 250 Films of 2023 with Female Directors')
plt.xlabel('Composer Gender', labelpad=15, fontweight='bold')
plt.ylabel('Percentage', fontweight='bold', rotation=0)
plt.gca().yaxis.set_label_coords(-0.1, 0.5)
plt.xticks(ticks=[0, 1, 2], labels=['Male', 'Unknown', 'Female'], rotation=0)
plt.show()

# Visualisation: Composer Gender when Directors = Male
plt.figure(figsize=(10, 6))
male_director_composer_breakdown.plot(kind='bar', color=['#5e25be', '#7b6603', '#07600d', '#a7a3a8'])
plt.title('Composer Gender Breakdown for Top 250 Films of 2023 with Male Directors')
plt.xlabel('Composer Gender', labelpad=15, fontweight='bold')
plt.ylabel('Percentage', fontweight='bold', rotation=0)
plt.gca().yaxis.set_label_coords(-0.1, 0.5)
plt.xticks(ticks=[0, 1, 2, 3], labels=['Male', 'Unknown', 'Female', 'Non-binary'], rotation=0)
plt.show()

# Visualisation: Average Vote Score by Director gender
plt.figure(figsize=(10, 6))
plt.bar(categories_vote, vote_averages, color=['#5e25be', '#07600d'])
plt.title('Average TMDB Scores for Top 250 Films of 2023')
plt.xlabel('Director Gender', labelpad=15, fontweight='bold')
plt.ylabel('Average\nVote\nScore', fontweight='bold', rotation=0)
plt.gca().yaxis.set_label_coords(-0.1, 0.5)
plt.ylim(0, 10)  # Vote averages typically range from 0 to 10
plt.xticks(rotation=0)
plt.show()
