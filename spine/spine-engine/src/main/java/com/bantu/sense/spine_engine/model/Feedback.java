package com.bantu.sense.spine_engine.model;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Entity
@Table(name = "user_feedback")
@Data
public class Feedback {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // CHANGE: Instead of a raw Long, we use the Inquiry Object
    @OneToOne // Why: Each piece of feedback belongs to exactly ONE inquiry
    @JoinColumn(name = "inquiry_id", nullable = false) // Why: This creates the Foreign Key in SQL
    private Inquiry inquiry;

    private Boolean isCorrect;

    private String correctedIntent;

    @Column(columnDefinition = "TEXT")
    private String userComments;

    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
    }
}