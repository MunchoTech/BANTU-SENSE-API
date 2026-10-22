package com.bantu.sense.spine_engine.controller;


import com.bantu.sense.spine_engine.dto.AnalysisResponse;
import com.bantu.sense.spine_engine.dto.InquiryRequest;
import com.bantu.sense.spine_engine.model.Inquiry;
import com.bantu.sense.spine_engine.service.InquiryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;


@RestController // Tells Spring this class handles web requests
@RequestMapping("/api/inquiries") // The "URL address" for this ear
@CrossOrigin(origins = "http://localhost:5173") // Allow your React app
public class InquiryController {

    @Autowired
    private InquiryService inquiryService;

    // This method listens for "POST" requests (sending data)
    // Create a small "Request" class or use a Map to grab the specific field
    @PostMapping("/send")
    public ResponseEntity<?> receiveInquiry(@RequestBody InquiryRequest input) {
        AnalysisResponse result = inquiryService.saveInquiry(input.getOriginalText(), input.isDonateForReview());
        if ("unavailable".equals(result.getStatus())) {
            return ResponseEntity.status(503).body(result);
        }
        return ResponseEntity.ok(result);
    }
    // This listens for "GET" requests (reading data)
    @GetMapping("/all")
    public ResponseEntity<java.util.List<Inquiry>> getAllInquiries() {
        // Repository.findAll() is a built-in magic trick from Spring Data JPA
        return ResponseEntity.ok(inquiryService.getAllInquiries());
    }
}
