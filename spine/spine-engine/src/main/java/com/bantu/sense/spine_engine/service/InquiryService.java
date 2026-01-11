package com.bantu.sense.spine_engine.service;



import com.bantu.sense.spine_engine.model.Inquiry;
import com.bantu.sense.spine_engine.repository.InquiryRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service // Tells Spring to manage this class as a "Bean"
public class InquiryService {

    @Autowired
    private InquiryRepository inquiryRepository;

    /**
     * This is where the business logic happens.
     * Later, this is where we will call our Python AI!
     */
    public Inquiry saveInquiry(String text) {
        // Validation: Don't save empty noise
        if (text == null || text.trim().isEmpty()) {
            throw new IllegalArgumentException("Nyanja text cannot be empty!");
        }

        // Create the object to be saved
        Inquiry inquiry = new Inquiry();
        inquiry.setOriginalText(text);

        // For now, we hardcode these until the AI Brain is connected
        inquiry.setDetectedIntent("PENDING_ANALYSIS");
        inquiry.setUrgencyLevel("UNKNOWN");

        // The "Hands" (Repository) save it to Postgres
        return inquiryRepository.save(inquiry);
    }
    public java.util.List<Inquiry> getAllInquiries() {
        return inquiryRepository.findAll();
    }
}