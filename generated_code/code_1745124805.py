import requests
from bs4 import BeautifulSoup

# URL of the website to scrape
url = 'https://www.example.com/news'

# Send a GET request to the URL
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Find all elements with the specified class that contains the news headlines
headlines = soup.find_all('h2', class_='headline')

# Extract and print the news headlines
for headline in headlines:
    print(headline.text)