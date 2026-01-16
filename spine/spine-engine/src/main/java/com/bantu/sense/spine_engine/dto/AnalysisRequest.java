package com.bantu.sense.spine_engine.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor // Why #3
public class AnalysisRequest {
    private String text;
}
