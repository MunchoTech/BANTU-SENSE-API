# 🇿🇲 Bantu-Sense-Core
**A Linguistic Intelligence Bridge for Zambian Services**

Bantu-Sense is an AI-powered backend designed to process and categorize citizen inquiries in local Zambian languages (Nyanja, Bemba, and Tonga). 

## 🏆 Day 16 Milestone: The Integrated Spine
As of Jan 16, 2026, the core engine is fully operational, linking a Java Spring Boot "Spine" with a Python "Brain" running the **Afro-XLM-R** model.

### 🌟 Key Features
- **Cross-Lingual Classification:** High-accuracy intent detection for Medical, Legal, and Financial inquiries.
- **Confidence Scoring:** Every AI response includes a precision percentage (e.g., *99.61% for Medical*).
- **Architectural Resilience:** Implemented a "Safe-Fail" mechanism that queues inquiries as `PENDING_ANALYSIS` if the AI microservice is temporarily offline.
- **Clean Data Pipeline:** Automatic extraction of raw linguistic text from JSON payloads.

### 🛠 Tech Stack
- **Backend:** Java 17 / Spring Boot 3
- **AI Microservice:** Python 3.10 / FastAPI
- **Model:** Afro-XLM-R (Transformers)
- **Database:** PostgreSQL
- **Environment:** Arch Linux 

### 📊 Live Test Result Example
```json
{
  "id": 7,
  "originalText": "Mumala mubaba",
  "detectedIntent": "MEDICAL",
  "confidenceScore": 99.61,
  "urgencyLevel": "ROUTINE (5/10)"
}
