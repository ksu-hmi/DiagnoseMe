from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__, template_folder='project/templates')

app = Flask(__name__)

# Function to scrape data from a URL
def scrape_website(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Assuming diseases are listed in hyperlinks under the "Directory: Guidance on prevention and control" section
        disease_links = soup.select('div#content div.main-content a')
        diseases = [link.get_text() for link in disease_links]
        return {'diseases': diseases}
    else:
        return None

# Sample list of symptoms
sample_symptoms = [
    'fever',
    'cough',
    'headache',
    # Add more symptoms as needed
]

# Base URL for scraping
base_url = "https://www.ecdc.europa.eu/en/all-topics"

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_symptoms = request.form.getlist('symptoms')
        # Define the URLs to scrape
        urls = [base_url]

        # Scrape data from the URLs
        scraped_data = []
        for url in urls:
            data = scrape_website(url)
            if data:
                scraped_data.append(data)

        # Filter diseases based on selected symptoms (dummy logic)
        filtered_diseases = []
        for disease in scraped_data[0].get('diseases', []):
            # Check if all selected symptoms are present in the disease name
            if all(symptom.lower() in disease.lower() for symptom in selected_symptoms):
                filtered_diseases.append(disease)

        return render_template('index.html', data=filtered_diseases, symptoms=sample_symptoms)

    return render_template('index.html', data=None, symptoms=sample_symptoms)

if __name__ == '__main__':
    app.run(debug=True)

