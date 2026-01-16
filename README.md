# 🇿🇲 BANTU-SENSE
### A Behavioral NLP Framework for Cognitive Justice and Digital Dignity

**Bantu-Sense** is a specialized AI-driven "Cultural Interpretability Layer" designed to bridge the linguistic gap in Zambia. By moving beyond literal word-swaps, this API utilizes **Behavioral Informatics** to ensure that low-resource languages (Nyanja, Bemba, Tonga) are no longer invisible in the digital economy.

---

## 🏆 UNZA Students Innovation Challenge 2026
**Applicant:** Robert Musomela  
**Category:** Innovation / ICT & Artificial Intelligence

## 🧠 The Core Innovation: The "Spine" & "Brain"
Bantu-Sense operates as a scalable API providing a specialized interface for:
1. **AI Intent Classification:** Categorizing citizen inquiries into **Medical, Legal, and Financial** domains.
2. **Behavioral Urgency Scoring:** An inference engine that analyzes linguistic markers to assign a 1–10 "Urgency Score."
3. **Context-Aware Semantic Mapping:** Leveraging **Afro-XLM-R** to understand the "how" and "why" of Zambian dialects.



## 🏗️ Technical Implementation
This repository contains the **Core Engine**, structured as a high-resilience microservice architecture:
- **The Spine (Java/Spring Boot):** Manages RESTful pathways, transaction persistence, and system-wide resilience.
- **The Brain (Python/FastAPI):** Orchestrates deep-learning inference and intent detection.
- **The Memory (PostgreSQL):** Stores linguistic data and audit trails for continuous model refinement.

## 🛡️ Resilience & Ethical Design
- **Lean Hardware Optimization:** Designed to run efficiently without massive server overhead.
- **Operational Resilience:** If the AI inference engine is unreachable, the Spine queues inquiries as `PENDING_ANALYSIS`, ensuring no Zambian voice is lost due to technical downtime.

## 📊 Real-Time API Response (Current Build)
```json
{
  "id": 8,
  "originalText": "Nifuna kutsegula account ya banki",
  "detectedIntent": "FINANCIAL",
  "confidenceScore": 86.68,
  "urgencyLevel": "ROUTINE (5/10)"
}
