package com.bantu.sense.spine_engine.service;

import com.bantu.sense.spine_engine.dto.AnalysisRequest;
import com.bantu.sense.spine_engine.dto.AnalysisResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class AIService {

    @Autowired // Why #4
    private RestTemplate restTemplate;

    private final String PYTHON_URL = "http://localhost:8000/analyze";


    // Inside your AIService class...

    public AnalysisResponse callPythonAI(String nyanjaText) {
        AnalysisRequest request = new AnalysisRequest(nyanjaText);

        try {
            // This is the attempt to talk to Python
            return restTemplate.postForObject(PYTHON_URL, request, AnalysisResponse.class);
        } catch (Exception e) {
            // This is the "Safety Net" that catches the "Storm"
            System.out.println("CRITICAL: Python Brain is unreachable. Activating Fallback.");

            AnalysisResponse fallback = new AnalysisResponse();
            fallback.setStatus("offline");
            fallback.setIntent("PENDING_ANALYSIS");
            fallback.setUrgency_score("QUEUED");
            fallback.setMessage("System is currently in offline mode due to connectivity.");

            return fallback;
        }
    }
}