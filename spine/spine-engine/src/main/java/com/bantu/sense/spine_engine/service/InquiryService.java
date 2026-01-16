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

    public Inquiry saveInquiry(String text) {
        Inquiry inquiry = new Inquiry();
        inquiry.setOriginalText(text);

        // 1. Get the suitcase back from Python
        AnalysisResponse aiResult = aiService.callPythonAI(text);

        // 2. Map the data (The missing link is here!)
        inquiry.setDetectedIntent(aiResult.getIntent());
        inquiry.setUrgencyLevel(aiResult.getUrgency_score());

        // NEW: Clean the "%" sign and save the number
        if (aiResult.getConfidence() != null) {
            String cleanConfidence = aiResult.getConfidence().replace("%", "");
            inquiry.setConfidenceScore(Double.parseDouble(cleanConfidence));
        }

        return inquiryRepository.save(inquiry);
    }

   /* public Inquiry saveInquiry(String text) {
        // 1. Validation...

        Inquiry inquiry = new Inquiry();
        inquiry.setOriginalText(text);

        // 2. Call the Bridge and get the full response object
        AnalysisResponse aiResult = aiService.callPythonAI(text);

        // 3. Map the Python data to your Java Entity
        inquiry.setDetectedIntent(aiResult.getIntent());
        inquiry.setUrgencyLevel(aiResult.getUrgency_score());
        // Pro-Tip: You could add a 'confidence' column to your Inquiry entity too!

        return inquiryRepository.save(inquiry);
    }*/

    public java.util.List<Inquiry> getAllInquiries() {
        return inquiryRepository.findAll();
    }

}