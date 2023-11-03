from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__, template_folder='project/templates')

app = Flask(__name__)

# Function to scrape data from a URL
def scrape_website(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string
        links = soup.find_all('a')
        return {'title': title, 'links': [(link.text, link.get('href')) for link in links]}
    else:
        return None

# Routes
@app.route('/')
def index():
    # Define the URLs to scrape
    urls = [
        "https://www.ecdc.europa.eu/en/all-topics",
        "https://www.ecdc.europa.eu/en/all-topics",
    ]

    # Scrape data from the URLs
    scraped_data = []
    for url in urls:
        data = scrape_website(url)
        if data:
            scraped_data.append(data)

    return render_template('index.html', data=scraped_data)

if __name__ == '__main__':
    app.run(debug=True)