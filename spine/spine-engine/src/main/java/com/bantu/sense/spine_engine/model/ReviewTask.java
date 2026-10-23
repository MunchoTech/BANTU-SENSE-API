package com.bantu.sense.spine_engine.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "review_tasks")
@Getter
@Setter
@NoArgsConstructor
public class ReviewTask {
    @Id
    @Column(length = 24)
    private String sampleId;

    @Column(nullable = false, length = 16)
    private String language;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String phrase;
}
