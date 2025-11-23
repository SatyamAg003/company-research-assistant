import requests
from duckduckgo_search import DDGS
import wikipedia

# Set a user agent for Wikipedia to avoid issues
wikipedia.set_user_agent("CompanyResearchBot/1.0")

def fetch_wikipedia_summary(company):
    try:
        # Search for the page first to handle disambiguation
        search_results = wikipedia.search(company)
        if not search_results:
            return {"source": "wikipedia", "error": "No Wikipedia page found"}
        
        page = wikipedia.page(search_results[0], auto_suggest=True)
        return {
            "source": "wikipedia",
            "title": page.title,
            "summary": page.summary[:500] + "..." if len(page.summary) > 500 else page.summary,
            "url": page.url
        }
    except wikipedia.DisambiguationError as e:
        try:
            # Try the first option from disambiguation
            page = wikipedia.page(e.options[0])
            return {
                "source": "wikipedia",
                "title": page.title,
                "summary": page.summary[:500] + "..." if len(page.summary) > 500 else page.summary,
                "url": page.url,
                "note": f"Disambiguated from {company} to {e.options[0]}"
            }
        except Exception as e2:
            return {"source": "wikipedia", "error": f"Disambiguation error: {str(e)}"}
    except Exception as e:
        return {"source": "wikipedia", "error": str(e)}

def fetch_duckduckgo(company, max_results=5):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(company, max_results=max_results))
            return {"source": "duckduckgo", "results": results}
    except Exception as e:
        return {"source": "duckduckgo", "error": str(e)}

def fetch_gnews(company, api_key, max_results=5):
    if not api_key:
        return {"source": "gnews", "error": "Missing API key."}

    url = "https://gnews.io/api/v4/search"
    params = {
        "q": company,
        "token": api_key,
        "lang": "en",
        "max": max_results
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        return {"source": "gnews", "articles": data.get("articles", [])}
    except Exception as e:
        return {"source": "gnews", "error": str(e)}