package com.bantu.sense.spine_engine.dto;

import java.util.List;

public record ReviewQueueResponse(List<ReviewTaskResponse> tasks, List<String> completedSampleIds) {
}
