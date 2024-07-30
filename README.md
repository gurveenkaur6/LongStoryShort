# LongStoryShort
LongStoryShort leverages Cohere for advanced text summarization and LangGraph for streamlined data workflows. This app fetches, summarizes, and analyzes news articles, extracting key entities and providing Google search links for further exploration.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Keys](#api-keys)
- [How It Works](#how-it-works)

## Features

- Fetches latest news articles based on user input.
- Summarizes news articles using Cohere's text summarization model.
- Extracts entities from summarized text with SpaCy.
- Provides Google search links for extracted entities.
- Interactive web app built with Streamlit.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/LongStoryShort.git
    ```

2. Navigate to the project directory:

    ```bash
    cd LongStoryShort
    ```

3. Create a virtual environment and activate it:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

4. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Create a `.env` file and add your API keys:

    ```
    NEWS_API_KEY=your_news_api_key
    COHERE_API_KEY=your_cohere_api_key
    ```

## Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

1. Open your browser and navigate to http://localhost:8501.
2. Enter a news topic and click "Summarize."
3. View fetched articles, their summaries, and linked entities.


## API Keys

- **NEWS_API_KEY**: Get it from [NewsAPI](https://newsapi.org/).
- **COHERE_API_KEY**: Obtain from [Cohere](https://cohere.ai/).

## How It Works

1. **Fetch News**: Retrieves articles based on user input.
2. **Summarize Text**: Uses Cohere to generate concise summaries.
3. **Extract Entities**: Identifies key entities from summaries using SpaCy.
4. **Link Entities**: Provides Google search links for each entity.
5. **Display Results**: Shows articles, summaries, entities, and search links on the Streamlit app.
