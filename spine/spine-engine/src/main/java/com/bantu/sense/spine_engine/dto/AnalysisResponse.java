package com.bantu.sense.spine_engine.dto;

import lombok.Data;

@Data
public class AnalysisResponse {
    private String status;
    private String intent;
    private String urgency_score; // Matches Python's "urgency_score"
    private String confidence;
    private String message; // For when Python is "uncertain"
}