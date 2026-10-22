package com.bantu.sense.spine_engine.service;



import com.bantu.sense.spine_engine.dto.AnalysisResponse;
import com.bantu.sense.spine_engine.model.Inquiry;
import com.bantu.sense.spine_engine.repository.InquiryRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class InquiryService {

    @Autowired
    private InquiryRepository inquiryRepository;

    @Autowired // NEW: We plug in the "Caller" we just built
    private AIService aiService;

    public AnalysisResponse saveInquiry(String text, boolean donateForReview) {
        Inquiry inquiry = new Inquiry();
        inquiry.setOriginalText(text);

        // 1. Get the suitcase back from Python
        AnalysisResponse aiResult = aiService.callPythonAI(text, donateForReview);

        // 2. Map the data (The missing link is here!)
        inquiry.setDetectedIntent(aiResult.getIntent());
        inquiry.setUrgencyLevel(aiResult.getUrgencyLevel());

        // NEW: Clean the "%" sign and save the number
        inquiry.setConfidenceScore(aiResult.getConfidence());

        inquiryRepository.save(inquiry);
        return aiResult;
    }

    public java.util.List<Inquiry> getAllInquiries() {
        return inquiryRepository.findAll();
    }

}
