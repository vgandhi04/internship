from fuzzywuzzy import process, fuzz

# List of movie names
movies = ["Titanic", "Avatar", "The Shawshank Redemption", "The Godfather", "Inception", "manic"]

# Search function using fuzzy matching
def search_movie(query, movie_list, threshold=50, limit=5):
    # Use process.extract to find matches with scores above threshold
    matches = process.extract(query, movie_list, scorer=fuzz.ratio, limit=limit)
    # Filter matches to include only those above threshold
    filtered_matches = [match[0] for match in matches if match[1] >= threshold]
    return filtered_matches

# Example usage
search_query = "manic"
matched_movies = search_movie(search_query, movies)
print(f"Search -- {search_query}")
print(f"Matches -- {matched_movies}")
