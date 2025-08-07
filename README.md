Ollama Powered Search EngineThis is a simple web application that uses a Python Flask backend to provide an AI-enhanced search experience. It scrapes search results from DuckDuckGo, then uses a local Ollama instance to re-rank and summarize the top results based on the user's query.FeaturesWeb Interface: A clean, modern UI built with React and Tailwind CSS.Web Scraping: Fetches initial search results from DuckDuckGo's HTML interface.AI-Powered Summarization: Connects to a local Ollama instance to intelligently process and summarize search results.Dynamic Model Selection: Automatically detects available Ollama models.Status Checking: Verifies that the Ollama server is online before allowing searches.Self-Contained: Runs locally with a Python backend, requiring no external cloud services (besides the search engine).PrerequisitesBefore you begin, ensure you have the following installed:Python 3.8+ and pip.Ollama: You must have a running Ollama instance.Download OllamaPull at least one model, for example: ollama pull llama3How to RunThere are two ways to run the application: using the automated script or setting it up manually.1. Automated Setup (Recommended)The run.sh script handles everything for you.Make the script executable:chmod +x run.sh
Run the script:./run.sh
This will create a virtual environment, install the necessary Python packages, and start the Flask server.2. Manual SetupCreate and activate a virtual environment:# Create the environment
python3 -m venv venv

# Activate it (on macOS/Linux)
source venv/bin/activate

# On Windows, use:
# venv\Scripts\activate
Install the required packages:pip install -r requirements.txt
Run the Flask application:python3 app.py
How to UseOnce the server is running, open your web browser and navigate to http://127.0.0.1:5000.The application will automatically check the status of your Ollama server.If the status indicator is green, you can type a query and press "Search".If the status is red, click the settings icon in the top-right to ensure the "Ollama Endpoint" URL is correct and that your Ollama server is running.Project Structure.
├── app.py              # The main Flask backend application
├── run.sh              # Automated setup and run script
├── requirements.txt    # Python dependencies
├── .gitignore          # Files and directories to be ignored by Git
└── templates/
    └── index.html      # The frontend HTML file with React/JS
