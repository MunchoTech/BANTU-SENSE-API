package com.bantu.sense.spine_engine.model;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Entity
@Table(name = "inquiries")
@Data // This is Lombok working for me
// !
public class Inquiry {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(columnDefinition = "TEXT", nullable = false)
    private String originalText;

    private String detectedIntent;

    private String urgencyLevel; // e.g., High, Medium, Low

    private Double confidenceScore;

    private LocalDateTime createdAt;


    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}

