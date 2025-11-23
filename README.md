Company Research Assistant 🤖

An intelligent AI-powered company research assistant that gathers information from multiple sources and generates comprehensive account plans through natural conversation with voice capabilities.

Features ✨
Chat-based Interface: Natural conversation like ChatGPT
Multi-source Research: Wikipedia, DuckDuckGo, and GNews API
Voice Input/Output: Speak your questions and hear responses
Account Plan Generation: Automatic creation of comprehensive business plans
Real-time Updates: Progress updates during research
Editable Plans: Modify any section of generated account plans
Export Options: Download as DOCX or copy to clipboard

Tech Stack 🛠️
Backend: FastAPI, Python, Uvicorn
Frontend: Streamlit
AI: Google Gemini API
APIs: Wikipedia, DuckDuckGo, GNews
Voice: SpeechRecognition, pyttsx3
Document Export: python-docx

Installation & Setup 🚀
Prerequisites
Python 3.8+
Google Gemini API key
GNews API key 

.env file structure should be :
GEMINI_API_KEY=your_actual_gemini_api_key
NEWSAPI_KEY=your_actual_gnews_api_key
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_URL=http://localhost:8000

To run the backend :
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

To start the streamlit frontend: 
streamlit run app.py

Data Flow Architecture
1. Research Request Flow
text
User Input → Frontend → Backend API → Data Fetchers → AI Synthesis → Response
     ↓           ↓           ↓           ↓               ↓           ↓
   Voice/Text   HTTP POST   Route       Wikipedia      Gemini      Formatted
     Input                 Handler     DuckDuckGo     Processing   Response
                           ↳ Validation GNews API
2. Account Plan Generation Flow
text
Research Data → Template Selection → AI Generation → Section Parsing → Editable UI
      ↓              ↓                 ↓                ↓              ↓
   Wikipedia      Pre-defined       Gemini Model    Regex-based     Streamlit
   DuckDuckGo     Sections          Prompt          Extraction      Text Areas
   GNews Data                       Engineering
3. Voice Processing Flow
text
Microphone → Speech Recognition → Text Processing → Backend API → Response → TTS
     ↓              ↓                  ↓              ↓            ↓        ↓
   Audio         Google Speech       Normalize      Same as      Formatted Voice
   Input           API               Input          Text Input   Response Output

Design Decisions:
FastAPI over Flask: Automatic docs, type hints, async support
Pydantic models: Request/response validation
CORS enabled: Frontend-backend communication
Sync over Async: Simpler error handling for external APIs
Separation of Concerns: Frontend handles UI/UX, backend handles business logic
Technology Flexibility: Can swap frontend/backend independently
Scalability: Backend can be scaled separately
Development Speed: Teams can work in parallel
Streamlit over React: Rapid prototyping, Python-native
Session State: Maintain conversation context
Component-based: Reusable UI elements

System Architecture Overview
text
┌─────────────────┐    HTTP/REST    ┌──────────────────┐    External APIs    ┌─────────────────┐
│   Streamlit     │◄───────────────►│   FastAPI        │◄───────────────────►│   Data Sources  │
│   Frontend      │                 │   Backend        │                     │                 │
│                 │                 │                  │                     │  ┌─────────────┐ │
│  - Chat UI      │                 │  - API Routes    │                     │  │ Wikipedia   │ │
│  - Voice I/O    │                 │  - Agent Logic   │                     │  └─────────────┘ │
│  - Plan Editor  │                 │  - Data Synthesis│                     │  ┌─────────────┐ │
└─────────────────┘                 └──────────────────┘                     │  │ DuckDuckGo  │ │
         │                                     │                              │  └─────────────┘ │
         │                              ┌──────┴──────┐                       │  ┌─────────────┐ │
         │                              │   Gemini    │                       │  │   GNews     │ │
         │                              │    AI       │                       │  └─────────────┘ │
         │                              └─────────────┘                       └─────────────────┘
    Browser-based
    User Interface

