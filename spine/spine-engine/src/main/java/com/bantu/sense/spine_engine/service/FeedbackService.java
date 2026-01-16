package com.bantu.sense.spine_engine.service;

import com.bantu.sense.spine_engine.model.Feedback;
import com.bantu.sense.spine_engine.model.Inquiry;
import com.bantu.sense.spine_engine.repository.FeedbackRepository;
import com.bantu.sense.spine_engine.repository.InquiryRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class FeedbackService {

    @Autowired
    private FeedbackRepository feedbackRepository;

    @Autowired
    private InquiryRepository inquiryRepository;

    public Feedback submitFeedback(Long inquiryId, Feedback feedback) {
        // 1. Find the Inquiry this feedback belongs to
        Inquiry inquiry = inquiryRepository.findById(inquiryId)
                .orElseThrow(() -> new RuntimeException("Inquiry not found with ID: " + inquiryId));

        // 2. Link them (The Foreign Key Handshake)
        feedback.setInquiry(inquiry);

        // 3. Save the feedback
        return feedbackRepository.save(feedback);
    }
}