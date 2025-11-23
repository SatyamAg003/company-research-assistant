import requests
import google.generativeai as genai
from .fetchers import fetch_wikipedia_summary, fetch_duckduckgo, fetch_gnews
from .config import GEMINI_API_KEY, NEWSAPI_KEY

def fetch_wikipedia_rest(company: str):
    """Fallback Wikipedia fetcher using REST API"""
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{company.replace(' ', '_')}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        return {
            "source": "wikipedia",
            "title": data.get("title", ""),
            "summary": data.get("extract", "No Wikipedia summary found."),
            "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
        }
    except Exception as e:
        return {"source": "wikipedia", "error": str(e)}

def fetch_duckduckgo_fallback(company: str):
    """Fallback DuckDuckGo fetcher"""
    try:
        url = f"https://api.duckduckgo.com/?q={company}&format=json&no_html=1&skip_disambig=1"
        r = requests.get(url, timeout=10)
        data = r.json()
        return {
            "source": "duckduckgo", 
            "results": [{
                "title": data.get("Heading", ""),
                "body": data.get("AbstractText", "No summary available"),
                "href": data.get("AbstractURL", "")
            }]
        }
    except Exception as e:
        return {"source": "duckduckgo", "error": str(e)}

def research_company(company, fetch_news=True):
    """Research a company and return raw data from all sources"""
    updates = []
    all_data = {}
    
    # Fetch data from multiple sources with progress updates
    updates.append(f"🔍 Starting research on {company}...")
    
    # Wikipedia
    updates.append("📚 Checking Wikipedia...")
    wiki_result = fetch_wikipedia_summary(company)
    if "error" in wiki_result:
        updates.append("⚠️ Wikipedia primary method failed, trying alternative...")
        wiki_result = fetch_wikipedia_rest(company)
    all_data["wikipedia"] = wiki_result
    
    # DuckDuckGo
    updates.append("🌐 Searching DuckDuckGo...")
    ddg_result = fetch_duckduckgo(company)
    if "error" in ddg_result:
        updates.append("⚠️ DuckDuckGo primary method failed, trying alternative...")
        ddg_result = fetch_duckduckgo_fallback(company)
    all_data["duckduckgo"] = ddg_result
    
    # News - Search for specific business terms
    news_result = {"source": "news", "articles": []}
    if fetch_news and NEWSAPI_KEY:
        # Search for company-specific business news
        updates.append("📰 Fetching business news from GNews...")
        
        # Try different search queries to get better results
        search_queries = [
            company,
            f"{company} orders",
            f"{company} contracts", 
            f"{company} business news"
        ]
        
        all_articles = []
        for query in search_queries:
            try:
                news_data = fetch_gnews(query, NEWSAPI_KEY)
                if "articles" in news_data:
                    all_articles.extend(news_data["articles"])
            except:
                continue
        
        # Remove duplicates based on title
        unique_articles = []
        seen_titles = set()
        for article in all_articles:
            title = article.get('title', '')
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)
        
        news_result["articles"] = unique_articles[:10]
        
        if "error" in news_result:
            updates.append("⚠️ GNews fetch encountered some issues")
        else:
            articles_count = len(news_result.get("articles", []))
            updates.append(f"✅ Found {articles_count} recent news articles")
    elif fetch_news and not NEWSAPI_KEY:
        updates.append("⚠️ GNews API key not configured - skipping news")
    all_data["news"] = news_result
    
    updates.append("✅ Research completed!")
    
    return {
        "updates": updates,
        "data": all_data,
        "company": company
    }

def generate_account_plan(company, research_data):
    """Generate a complete account plan from research data"""
    try:
        if not GEMINI_API_KEY:
            return {"error": "Gemini API key not configured"}
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("models/gemini-2.5-flash")

        # Prepare source text
        wiki_data = research_data.get('wikipedia', {})
        wiki_text = wiki_data.get('summary', 'No Wikipedia data available')
        
        ddg_data = research_data.get('duckduckgo', {})
        ddg_text = "No DuckDuckGo data"
        if ddg_data.get('results'):
            ddg_text = ddg_data['results'][0].get('body', 'No summary available')
            
        news_data = research_data.get('news', {})
        news_text = "No recent news found"
        if news_data.get('articles'):
            news_titles = [article.get('title', 'No title') for article in news_data['articles'][:3]]
            news_text = ", ".join(news_titles)

        prompt = f"""
Based on the research data below, create a COMPLETE account plan for {company} with the following sections:

1. EXECUTIVE SUMMARY: 4-5 sentence overview of the company
2. COMPANY OVERVIEW: Detailed background, history, and core business
3. KEY CONTACTS: Suggested key positions to target (since we don't have actual contacts)
4. STRENGTHS & WEAKNESSES: 3-4 key strengths and 2-3 weaknesses
5. OPPORTUNITIES & RISKS: 3-4 opportunities and 2-3 risks
6. ENGAGEMENT PLAN: Strategic approach for building relationship

RESEARCH DATA:
Wikipedia: {wiki_text}
DuckDuckGo: {ddg_text}
Recent News: {news_text}

Format your response exactly like this:

EXECUTIVE SUMMARY:
[Your executive summary here]

COMPANY OVERVIEW:
[Your company overview here]

KEY CONTACTS:
[Your key contacts analysis here]

STRENGTHS & WEAKNESSES:
[Your strengths and weaknesses analysis here]

OPPORTUNITIES & RISKS:
[Your opportunities and risks analysis here]

ENGAGEMENT PLAN:
[Your engagement plan here]

Make each section comprehensive and actionable.
"""

        response = model.generate_content(prompt)
        
        if response and hasattr(response, 'text'):
            return parse_account_plan(response.text)
        else:
            return {"error": "Failed to generate account plan"}
            
    except Exception as e:
        return {"error": f"Account plan generation failed: {str(e)}"}

def parse_account_plan(full_plan_text):
    """Parse the generated account plan into sections"""
    sections = {
        "executive_summary": "",
        "company_overview": "",
        "key_contacts": "",
        "strengths_weaknesses": "",
        "opportunities_risks": "",
        "engagement_plan": ""
    }
    
    current_section = None
    lines = full_plan_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this line is a section header
        if "EXECUTIVE SUMMARY" in line.upper():
            current_section = "executive_summary"
            continue
        elif "COMPANY OVERVIEW" in line.upper():
            current_section = "company_overview"
            continue
        elif "KEY CONTACTS" in line.upper():
            current_section = "key_contacts"
            continue
        elif "STRENGTHS" in line.upper() and "WEAKNESSES" in line.upper():
            current_section = "strengths_weaknesses"
            continue
        elif "OPPORTUNITIES" in line.upper() and "RISKS" in line.upper():
            current_section = "opportunities_risks"
            continue
        elif "ENGAGEMENT PLAN" in line.upper():
            current_section = "engagement_plan"
            continue
        
        # Add content to current section
        if current_section and line:
            sections[current_section] += line + "\n"
    
    # Clean up the sections
    for section in sections:
        sections[section] = sections[section].strip()
        if not sections[section]:
            sections[section] = f"Content for {section.replace('_', ' ').title()} will be generated."
    
    return sections

def generate_chat_response(user_message, conversation_history, research_data=None):
    """Generate conversational response using Gemini with ALL research data"""
    try:
        if not GEMINI_API_KEY:
            return "Gemini API key not configured. Please check your .env file."
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        
        # Build context from conversation history
        context = "Previous conversation:\n"
        for msg in conversation_history[-6:]:
            context += f"{msg['role']}: {msg['content']}\n"
        
        # Add research data if available
        research_context = ""
        if research_data:
            wiki_data = research_data.get('wikipedia', {})
            wiki_text = wiki_data.get('summary', 'No Wikipedia data available')
            
            ddg_data = research_data.get('duckduckgo', {})
            ddg_text = "No DuckDuckGo data available"
            if ddg_data.get('results'):
                ddg_text = ddg_data['results'][0].get('body', 'No summary available')
            
            news_data = research_data.get('news', {})
            news_articles = news_data.get('articles', [])
            
            if news_articles:
                news_text = "RECENT NEWS ARTICLES:\n"
                for i, article in enumerate(news_articles[:3], 1):
                    title = article.get('title', 'Untitled article')
                    news_text += f"{i}. {title}\n"
            else:
                news_text = "No recent news articles found."
            
            research_context = f"""
RESEARCH DATA FOR {research_data.get('company', 'THE COMPANY').upper()}:

WIKIPEDIA SUMMARY:
{wiki_text}

DUCKDUCKGO INFORMATION:
{ddg_text}

{news_text}
"""
        
        prompt = f"""
You are a helpful Company Research Assistant.

{research_context}

Current conversation:
{context}

User: {user_message}

Assistant: Respond conversationally and helpfully. 
- For questions about recent events, orders, contracts: PRIORITIZE the news articles
- For general company background: use Wikipedia and DuckDuckGo data
- If no research data is available, say so
- Keep responses natural but informative
"""

        response = model.generate_content(prompt)
        return response.text if response else "I apologize, but I couldn't generate a response."
        
    except Exception as e:
        return f"I encountered an error: {str(e)}"