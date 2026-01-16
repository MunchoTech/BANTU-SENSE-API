package com.bantu.sense.spine_engine.controller;


import com.bantu.sense.spine_engine.model. Inquiry;
import com.bantu.sense.spine_engine.service.InquiryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController // Tells Spring this class handles web requests
@RequestMapping("/api/inquiries") // The "URL address" for this ear
public class InquiryController {

    @Autowired
    private InquiryService inquiryService;

    // This method listens for "POST" requests (sending data)
    // Create a small "Request" class or use a Map to grab the specific field
    @PostMapping("/send")
    public ResponseEntity<?> receiveInquiry(@RequestBody Inquiry input) {
        Inquiry saved = inquiryService.saveInquiry(input.getOriginalText());

        // If the AI was offline, we inform the user
        if ("PENDING_ANALYSIS".equals(saved.getDetectedIntent())) {
            return ResponseEntity.accepted().body("Message received. We are processing it shortly.");
        }

        return ResponseEntity.ok(saved);
    }
    // This listens for "GET" requests (reading data)
    @GetMapping("/all")
    public ResponseEntity<java.util.List<Inquiry>> getAllInquiries() {
        // Repository.findAll() is a built-in magic trick from Spring Data JPA
        return ResponseEntity.ok(inquiryService.getAllInquiries());
    }
}
