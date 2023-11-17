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
        # Add more symptoms or keywords as needed
    ]

    selected_disease_urls = []

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
                    break  # Stop at the first matching symptom
                    
        no_diseases = not selected_disease_urls
        return render_template('index.html', selected_disease_urls=selected_disease_urls,
                               sample_symptoms=sample_symptoms, no_diseases=no_diseases)

    return render_template('index.html', selected_disease_urls=[], sample_symptoms=sample_symptoms, no_diseases=False)

if __name__ == '__main__':
    app.run(debug=True)
