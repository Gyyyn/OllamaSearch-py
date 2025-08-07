import requests
import json
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify
from urllib.parse import unquote, urlparse, parse_qs

# Initialize the Flask application
app = Flask(__name__)

# --- Helper Functions ---

def scrape_duckduckgo(query):
    """
    Scrapes DuckDuckGo for search results.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        # Use the HTML version of DuckDuckGo
        url = f"https://html.duckduckgo.com/html/?q={query}"
        # **MODIFIED**: Added a 10-second timeout to the request
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes

        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        # Find all result containers
        result_nodes = soup.find_all('div', class_='web-result')
        
        for node in result_nodes:
            title_anchor = node.find('a', class_='result__a')
            
            if title_anchor:
                title = title_anchor.get_text(strip=True)
                raw_link = title_anchor['href']
                
                # Clean the DDG redirect URL
                # The actual URL is in the 'uddg' query parameter
                parsed_url = urlparse(raw_link)
                uddg_param = parse_qs(parsed_url.query).get('uddg')
                
                link = unquote(uddg_param[0]) if uddg_param else raw_link
                
                results.append({'title': title, 'link': link})

        return results
    except requests.RequestException as e:
        print(f"Error scraping DuckDuckGo: {e}")
        return None


def query_ollama(prompt, endpoint, model):
    """
    Sends a prompt to the Ollama API and gets a ranked/summarized response.
    """
    try:
        print(f"Querying Ollama model {model} at {endpoint}")
        response = requests.post(
            f"{endpoint}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            # A longer timeout for the AI model to process
            timeout=60
        )
        response.raise_for_status()

        # The response from Ollama is a JSON object where the 'response' key
        # contains the actual JSON string we need.
        response_data = response.json()
        print(f"Ollama response: {response_data}")
        return json.loads(response_data.get('response', '{}'))

    except requests.RequestException as e:
        print(f"Error querying Ollama: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding Ollama's JSON response: {e}")
        print(f"Raw Ollama response: {response.text}")
        return None

# --- API Routes ---

@app.route('/')
def index():
    """
    Serves the main HTML page.
    """
    return render_template('index.html')


@app.route('/api/status', methods=['POST'])
def get_status():
    """
    Checks the status of the Ollama server and gets available models.
    """
    data = request.json
    endpoint = data.get('ollama_endpoint')
    if not endpoint:
        return jsonify({"error": "Ollama endpoint not provided"}), 400

    try:
        print(f"Checking Ollama status at {endpoint}")
        # **MODIFIED**: Added a 5-second timeout
        health_response = requests.get(endpoint, timeout=5)
        health_response.raise_for_status()
        if "Ollama is running" not in health_response.text:
             return jsonify({"online": False, "error": "Ollama is not running"}), 200

        # **MODIFIED**: Added a 5-second timeout
        tags_response = requests.get(f"{endpoint}/api/tags", timeout=5)
        tags_response.raise_for_status()
        models_data = tags_response.json()
        
        return jsonify({
            "online": True,
            "models": models_data.get('models', [])
        })
    except requests.RequestException as e:
        print(f"Error checking Ollama status: {e}")
        return jsonify({"online": False, "error": str(e)}), 200


@app.route('/api/search', methods=['POST'])
def search():
    """
    Handles the main search request from the frontend.
    """
    data = request.json
    query = data.get('query')
    ollama_endpoint = data.get('ollama_endpoint')
    ollama_model = data.get('ollama_model')

    if not all([query, ollama_endpoint, ollama_model]):
        return jsonify({"error": "Missing required parameters"}), 400

    # 1. Scrape DuckDuckGo
    scraped_results = scrape_duckduckgo(query)
    if scraped_results is None or not scraped_results:
        return jsonify({"error": "Failed to get results from DuckDuckGo. It may be temporarily unavailable or blocking requests."}), 500

    # 2. Build the prompt for Ollama
    prompt = f"""
        Based on the user query "{query}", please re-rank the following search results for relevance and provide a concise one-sentence summary for the top 5.
        
        Search Results (JSON format):
        {json.dumps(scraped_results[:10])}

        Your task:
        1. Analyze the user query and the content of each search result title.
        2. Determine the top 5 most relevant results.
        3. For each of the top 5, write a single, compelling summary sentence.
        4. Return ONLY a JSON array of objects, with each object containing "title", "link", and "summary" keys. Do not include any other text, explanations, or markdown formatting. The output must be valid JSON.
    """

    # 3. Query Ollama
    final_results = query_ollama(prompt, ollama_endpoint, ollama_model)
    if final_results is None:
        return jsonify({"error": "Failed to get a valid response from Ollama. The model may be taking too long or returned an invalid format."}), 500
    
    return jsonify(final_results)


# --- Main execution ---

if __name__ == '__main__':
    # Running on 0.0.0.0 makes it accessible on your local network
    app.run(host='0.0.0.0', port=5000, debug=True)
