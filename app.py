from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import concurrent.futures
from urllib.parse import urljoin

app = Flask(__name__)

def extract_disease_urls():
    base_url = "https://www.nhsinform.scot/illnesses-and-conditions/a-to-z/"
    response = requests.get(base_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        disease_links = soup.select(".az_list_indivisual a")
        base_url = "https://www.nhsinform.scot"
        return [urljoin(base_url, link['href']) for link in disease_links]
    else:
        return []

def check_symptom_for_url(url, symptom):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        page_text = soup.get_text().lower()
        return symptom.lower() in page_text

@app.route('/', methods=['GET', 'POST'])
def index():
    sample_symptoms = [
        'pale skin',
        'tiredness',
        'breathlessness',
        'infections',
        'bleeding',
        'cough',
        'fever',
        'nausea',
        'vomiting',
        'diarrhea',
        'constipation',
        'headache',
        'joint pain',
        'muscle pain',
        'abdominal pain',
        'chest pain',
        'back pain',
        'fatigue',
        'dizziness',
        'swelling',
        'weight loss',
        'weight gain',
        'rash',
        'sore throat',
        'difficulty swallowing',
        'vision problems',
        'hearing loss',
        'numbness',
        'tingling',
        'seizures'
        # Add more symptoms as needed
    ]

    selected_disease_urls = []
    selected_symptoms = []  # Initialize an empty list to hold selected symptoms

    if request.method == 'POST':
        selected_symptoms = request.form.getlist('symptoms')
        disease_urls = extract_disease_urls()

        if not disease_urls:
            return render_template('index.html', selected_disease_urls=[], sample_symptoms=sample_symptoms, no_diseases=True)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(check_symptom_for_url, url, symptom): (url, symptom) for url in disease_urls for symptom in selected_symptoms}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    selected_disease_urls.append(futures[future][0])
                    # Commenting out 'break' to find all matching symptoms instead of stopping at the first match

        no_diseases = not selected_disease_urls
        return render_template('index.html', selected_disease_urls=selected_disease_urls,
                               sample_symptoms=sample_symptoms, no_diseases=no_diseases, selected_symptoms=selected_symptoms)

    return render_template('index.html', selected_disease_urls=[], sample_symptoms=sample_symptoms, no_diseases=False, selected_symptoms=selected_symptoms)
if __name__ == '__main__':
    app.run(debug=True)
