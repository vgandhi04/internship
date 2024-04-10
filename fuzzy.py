from fuzzywuzzy import fuzz

# List of movie names
movies = ["Titanic", "Avatar", "The Shawshank Redemption", "The Godfather", "Inception", "manic"]

# Search function using fuzzy matching
def search_movie(query, movie_list, threshold=50):
    # Initialize list to store matching movie names
    matches = []
    
    # Iterate through movie list to find matches above threshold
    for movie in movie_list:
        # Calculate similarity score between query and movie name
        score = fuzz.ratio(query.lower(), movie.lower())
        # print(f"Score - {score} - movie - {movie}")
        # If score is above threshold, add movie to matches list
        if score >= threshold:
            matches.append(movie)
    
    # Return list of matches
    return matches

# Example usage
search_query = "manic"
matched_movies = search_movie(search_query, movies)
print(f"Search -- {search_query}")
print(f"Matches -- {matched_movies}")
