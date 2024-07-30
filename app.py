import cohere
import os
import requests
from dotenv import load_dotenv
import spacy
from langgraph.graph import Graph
from langchain_community.tools.tavily_search import TavilySearchResults

import streamlit as st
from langgraph.graph import Graph
from langchain.llms import Cohere

# Load environment variables from .env file
load_dotenv()
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
os.environ["COHERE_API_KEY"] = os.getenv("COHERE_API_KEY")

# Initialize the Cohere client for text generation
co = cohere.Client(os.getenv('COHERE_API_KEY'))


# Load SpaCy model for named entity recognition
## using spacy, we can extract key entities from the news such as persons, organizations, locations, dates, etc. 
nlp = spacy.load('en_core_web_sm')


## Fetch articles by making an HTTP request to NewsAPI.
def fetch_news(query):
    url = f'https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    data = response.json()

    # Check if the response is successful and contains articles
    if response.status_code == 200 and 'articles' in data:
        articles = data['articles']
        return articles[:10]
    else:
        print(f"Error fetching news: {data.get('message', 'Unknown error')}")
        return []

# function to extract named entities from text using SpaCy
def extract_entities(text):
    if text is None:
        return []
    doc = nlp(text)
    entities = []

    # Iterate through SpaCy's identified entities
    for ent in doc.ents:
        
        # Concatenate multi-word entities to ensure they are kept together
        entity_text = ent.text
        if entities and entities[-1][0] == entity_text:
            # If the entity is a multi-word entity, keep it together
            entities[-1] = (entities[-1][0] + " " + entity_text, ent.label_)
        else:
            entities.append((entity_text, ent.label_))
    return entities

## Using Cohere's text summarization model to generate summaries of the articles.
def summarize_text(text):

    response = co.generate(
        model='command-xlarge-nightly',
        prompt=f"Summarize the following article: {text}",
        max_tokens=100, # limit summary length
        temperature=0.5 # Set temperature for randomness
    )
    summary = response.generations[0].text.strip() # Extract summary text
    return summary

# to create Google search links for entities
def link_entities_to_google(entities):
    google_entities = []
    for entity, label in entities:
        search_query = entity
        google_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        google_entities.append((entity, label, google_url))
    return google_entities

# NODE 1 : Fetches news articles based on the user query.
def fetch_news_node(state):
    query = state['query']
    articles = fetch_news(query)
    articles=[article for article in articles if article.get('description') != '[Removed]']
    articles = articles[:10] # Limit to top 10 articles
    state['articles'] = articles
    return state

# Summarizes the text of each of the fetched articles.
def summarize_text_node(state):
    articles = state['articles']
    # Initialize summaries list
    summaries = []

    # Summarize the description of each article
    for article in articles:
        description = article.get('description')
        if description:
            summary = summarize_text(description)
            summaries.append(summary)
        else:
            summaries.append("Summary not available")
    state['summaries'] = summaries
    return state

# Extracts entities from the summarized text.
def extract_entities_node(state):
    summaries = state['summaries']
    entities = [extract_entities(summary) for summary in summaries]
    state['entities'] = entities
    return state

# Link extracted entities to Google search
def link_entities_node(state):
    all_linked_entities = []
    for entities in state['entities']:
        linked_entities = link_entities_to_google(entities)
        all_linked_entities.append(linked_entities)
    state['linked_entities'] = all_linked_entities
    return state

# Define the workflow using LangGraph
workflow = Graph()

# Define nodes of the graph
workflow.add_node('fetch_news', fetch_news_node)
workflow.add_node('extract_entities', extract_entities_node)
workflow.add_node('summarize_text', summarize_text_node)
workflow.add_node('link_entities', link_entities_node)

# conect the graph
workflow.add_edge('fetch_news', 'extract_entities')
workflow.add_edge('extract_entities', 'summarize_text')
workflow.add_edge('summarize_text', 'link_entities')

# Set entry and finish points
workflow.set_entry_point('fetch_news')
workflow.set_finish_point('link_entities')

app = workflow.compile()

# Streamlit app
# Streamlit app
def main():
    st.title("LongStoryShort")
    st.write("Enter a topic to fetch and get the summary of the latest news articles.")
    
    query = st.text_input("Enter a news topic", "")
    if st.button("Summarize"):
        if query:
            state = {"query": query}
            
            # Execute the workflow
            st.write("Fetching news articles...")
            state = fetch_news_node(state)

            if state['articles']:

                st.write("Summarizing articles...")
                state = summarize_text_node(state)

                st.write("Extracting entities from summaries...")
                state = extract_entities_node(state)

                st.write("Linking entities to Google Search...")
                state = link_entities_node(state)

                for i, article in enumerate(state['articles']):
                    description = article.get('description')
                    if description:
                        st.subheader(f"{i + 1}. {article['title']}")
                        st.write(description)
                        st.subheader(f"Summary of Article {i + 1}")
                         # Check if index is within bounds
                        if i < len(state['summaries']):
                            st.write(state['summaries'][i])
                        else:
                            st.write("Summary not available")
                        st.write(f"Entities: {state['entities'][i]}")
                        for entity, label, google_url in state['linked_entities'][i]:
                            st.write(f"- **{entity}** ({label}): [Google Search]({google_url})")
                
                st.write("Workflow complete.")
            else:
                st.write("No articles found for the given topic.")
        else:
            st.write("Please enter a topic to fetch news articles.")

if __name__ == "__main__":
    main()


