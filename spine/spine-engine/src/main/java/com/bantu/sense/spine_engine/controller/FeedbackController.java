package com.bantu.sense.spine_engine.controller;

import com.bantu.sense.spine_engine.model.Feedback;
import com.bantu.sense.spine_engine.service.FeedbackService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/feedback")
public class FeedbackController {

    @Autowired
    private FeedbackService feedbackService;

    @PostMapping("/submit/{inquiryId}")
    public ResponseEntity<Feedback> submitFeedback(
            @PathVariable Long inquiryId,
            @RequestBody Feedback feedback) {
        return ResponseEntity.ok(feedbackService.submitFeedback(inquiryId, feedback));
    }
}