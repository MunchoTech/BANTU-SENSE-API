package com.bantu.sense.spine_engine.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

@Service
public class ReviewAccessService {
    private final String accessCode;

    public ReviewAccessService(@Value("${bantu.review.access-code:}") String accessCode) {
        this.accessCode = accessCode;
    }

    public void requireAccess(String suppliedCode) {
        requireMatchingCode(suppliedCode, accessCode, "Review");
    }

    public void requireAdminAccess(String suppliedCode, String adminCode) {
        requireMatchingCode(suppliedCode, adminCode, "Review results");
    }

    private static void requireMatchingCode(String suppliedCode, String configuredCode, String label) {
        if (configuredCode.isBlank()) {
            throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE,
                    label + " access has not been configured by the project owner.");
        }
        if (suppliedCode == null || !MessageDigest.isEqual(
                configuredCode.getBytes(StandardCharsets.UTF_8),
                suppliedCode.getBytes(StandardCharsets.UTF_8))) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "The access code is not correct.");
        }
    }
}
