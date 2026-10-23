package com.bantu.sense.spine_engine.controller;

import com.bantu.sense.spine_engine.dto.ReviewQueueResponse;
import com.bantu.sense.spine_engine.dto.ReviewSubmissionRequest;
import com.bantu.sense.spine_engine.service.ReviewAccessService;
import com.bantu.sense.spine_engine.service.ReviewService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/review")
@CrossOrigin(origins = "${bantu.web.allowed-origin:http://localhost:5173}")
public class ReviewController {
    private final ReviewAccessService accessService;
    private final ReviewService reviewService;
    private final String adminCode;

    public ReviewController(ReviewAccessService accessService, ReviewService reviewService,
                            @Value("${bantu.review.admin-code:}") String adminCode) {
        this.accessService = accessService;
        this.reviewService = reviewService;
        this.adminCode = adminCode;
    }

    @GetMapping("/tasks")
    public ResponseEntity<ReviewQueueResponse> getTasks(
            @RequestHeader(value = "X-Review-Access-Code", required = false) String accessCode,
            @RequestHeader(value = "X-Reviewer-Code", required = false) String reviewerCode) {
        accessService.requireAccess(accessCode);
        return ResponseEntity.ok(reviewService.getQueue(reviewerCode));
    }

    @PostMapping("/submissions")
    public ResponseEntity<Void> submit(
            @RequestHeader(value = "X-Review-Access-Code", required = false) String accessCode,
            @RequestBody ReviewSubmissionRequest request) {
        accessService.requireAccess(accessCode);
        reviewService.submit(request);
        return ResponseEntity.status(HttpStatus.CREATED).build();
    }

    @GetMapping(value = "/results.csv", produces = "text/csv")
    public ResponseEntity<byte[]> downloadResults(
            @RequestHeader(value = "X-Review-Admin-Code", required = false) String suppliedAdminCode) {
        accessService.requireAdminAccess(suppliedAdminCode, adminCode);
        byte[] csv = reviewService.exportResultsCsv().getBytes(java.nio.charset.StandardCharsets.UTF_8);
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=review-responses.csv")
                .contentType(new MediaType("text", "csv", java.nio.charset.StandardCharsets.UTF_8))
                .body(csv);
    }
}
