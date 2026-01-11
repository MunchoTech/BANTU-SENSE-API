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
    @PostMapping("/send")
    public ResponseEntity<Inquiry> receiveInquiry(@RequestBody String nyanjaText) {
        // We pass the text to our Service to handle the logic
        Inquiry savedInquiry = inquiryService.saveInquiry(nyanjaText);

        // Return the saved object so the user knows it worked
        return ResponseEntity.ok(savedInquiry);
    }
}
