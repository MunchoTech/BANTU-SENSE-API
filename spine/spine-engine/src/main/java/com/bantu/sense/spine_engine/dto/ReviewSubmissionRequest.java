package com.bantu.sense.spine_engine.dto;

public record ReviewSubmissionRequest(
        String sampleId,
        String reviewerCode,
        String languageCheck,
        String intentLabel,
        String naturalness,
        String notes
) {
}
