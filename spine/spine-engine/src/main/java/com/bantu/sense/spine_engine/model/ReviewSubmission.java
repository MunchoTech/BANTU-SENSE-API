package com.bantu.sense.spine_engine.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

@Entity
@Table(name = "review_submissions", uniqueConstraints = {
        @UniqueConstraint(name = "uk_review_task_reviewer", columnNames = {"task_id", "reviewer_code"})
})
@Getter
@Setter
@NoArgsConstructor
public class ReviewSubmission {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "task_id", nullable = false)
    private ReviewTask task;

    @Column(name = "reviewer_code", nullable = false, length = 24)
    private String reviewerCode;

    @Column(name = "language_check", nullable = false, length = 16)
    private String languageCheck;

    @Column(name = "intent_label", nullable = false, length = 16)
    private String intentLabel;

    @Column(nullable = false, length = 16)
    private String naturalness;

    @Column(columnDefinition = "TEXT")
    private String notes;

    @Column(nullable = false)
    private LocalDateTime submittedAt;

    @jakarta.persistence.PrePersist
    protected void onCreate() {
        submittedAt = LocalDateTime.now();
    }
}
