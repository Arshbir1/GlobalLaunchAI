GlobalLaunch AI
Overview
GlobalLaunch AI is an AI-powered platform that helps startups identify optimal countries for expansion based on their product, industry, or business plan. It uses MongoDB Atlas Vector Search, Google Cloud Vertex AI/Document AI, and public datasets to provide market insights, regulatory analysis, and risk scores. Each top country includes detailed insight cards: market opportunity, regulatory compliance, risk analysis, trade incentives, expansion guide, and localized considerations. Features include a multilingual chatbot, RAG system for regulation Q&A, and PDF uploads. The frontend is a basic HTML/CSS/JS site for testing, with a focus on backend functionality.
Setup

Backend:
Install dependencies: pip install -r backend/requirements.txt
Set environment variables in backend/.env
Run: uvicorn backend.app.main:app --reload
Preprocess data: python backend/scripts/preprocess_data.py
Preprocess regulatory texts: python backend/scripts/regulatory_data.py


Frontend:
Serve frontend folder using npx serve frontend.
Replace YOUR_GOOGLE_MAPS_API_KEY in index.html.


MongoDB:
Create a cluster, enable Vector Search.
Create indexes: vector_index on countries.embedding, regulatory_vector_index on regulations.embedding, and pdfs collection.


Google Cloud:
Enable Vertex AI, Document AI, and Maps APIs.
Set up service account credentials.



Tech Stack

Backend: FastAPI, MongoDB Atlas, Google Cloud Vertex/Document AI, PyPDF2
Frontend: HTML, CSS, JavaScript, TailwindCSS (CDN), i18next, FilePond, Google Maps API
Data: World Bank GDPR, OECD, WTO, UN, GSMA, Transparency, IMF
Features:
Product idea and PDF analysis
Multilingual chatbot (English, Spanish, French, German)
RAG system for regulation Q&A
Interactive map with insight cards
Detailed country-specific insights (market, regulatory, risk, etc.)



Deployment

Deploy via ./deploy.sh (Vercel for backend and static frontend).
Configure Google Cloud Storage or Vercel Blob for PDF uploads.

