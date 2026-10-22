package com.bantu.sense.spine_engine.dto;

import lombok.Data;

@Data
public class AnalysisResponse {
    private String status;
    private String intent;
    private Double confidence;
    private Integer urgencyScore;
    private String urgencyLevel;
    private boolean reviewSubmitted;
    private String message;
    private String semanticContext;
}
