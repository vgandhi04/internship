import requests
from bs4 import BeautifulSoup
import time

def fetch_cricket_scores():
    # Make a request to the Cricbuzz website
    response = requests.get('https://www.cricbuzz.com/')

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the live matches section
    live_matches_section = soup.find('div', {'class': 'cb-col cb-col-100 cb-ltst-wgt-hdr'})

    if live_matches_section:
        # Extract the match details
        match_details = live_matches_section.find_all('div', {'class': 'cb-col cb-col-100 cb-mtch-blk'})

        # Print the match details
        for match in match_details:
            team1 = match.find('div', {'class': 'cb-ovr-flo'}).text.strip()
            team2 = match.find('div', {'class': 'cb-series-b'}).text.strip()
            score = match.find('div', {'class': 'cb-ltst-wgt-val'}).text.strip()
            print(f"{team1} vs {team2}: {score}")
    else:
        print("Could not find the live matches section on the Cricbuzz website.")
        
if __name__ == '__main__':
    while True:
        fetch_cricket_scores()
        print('Scores updated. Waiting for 5 minutes...')
        time.sleep(10)  # Wait for 5 minutes (300 seconds)