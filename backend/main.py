from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .config import GEMINI_API_KEY, NEWSAPI_KEY, BACKEND_HOST, BACKEND_PORT
from .agent import research_company, generate_chat_response, generate_account_plan

class ResearchBody(BaseModel):
    company: str
    fetch_news: bool = True

class ChatBody(BaseModel):
    message: str
    conversation_history: list = []

class AccountPlanBody(BaseModel):
    company: str
    research_data: dict

app = FastAPI(title="Company Research Assistant API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store research data in memory
research_cache = {}

@app.get("/")
def read_root():
    return {"message": "Company Research Assistant API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/research")
def api_research(body: ResearchBody):
    try:
        result = research_company(
            company=body.company,
            fetch_news=body.fetch_news
        )
        # Cache the research data
        research_cache[body.company.lower()] = result["data"]
        return result
    except Exception as e:
        return {
            "updates": [f"Error: {str(e)}"],
            "data": {},
            "company": body.company
        }

@app.post("/api/chat")
def api_chat(body: ChatBody):
    try:
        # Check if we have research data for any mentioned company
        research_data = None
        for company in research_cache:
            if company in body.message.lower():
                research_data = research_cache[company]
                research_data["company"] = company
                break
        
        response = generate_chat_response(
            user_message=body.message,
            conversation_history=body.conversation_history,
            research_data=research_data
        )
        
        return {
            "response": response,
            "research_available": research_data is not None
        }
        
    except Exception as e:
        return {
            "response": f"Sorry, I encountered an error: {str(e)}",
            "research_available": False
        }

@app.post("/api/generate-account-plan")
def api_generate_account_plan(body: AccountPlanBody):
    try:
        account_plan = generate_account_plan(body.company, body.research_data)
        return account_plan
    except Exception as e:
        return {"error": f"Failed to generate account plan: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=BACKEND_HOST, port=BACKEND_PORT)