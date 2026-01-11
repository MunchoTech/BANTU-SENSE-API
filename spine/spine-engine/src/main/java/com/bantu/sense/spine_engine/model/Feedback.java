package com.bantu.sense.spine_engine.model;


import jakarta.persistence.*;
import lombok.Data;

@Entity
@Table(name = "user_feedback")
@Data
public class Feedback {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Long inquiryId; // Reference to the original inquiry

    private Boolean isCorrect;

    private String correctedIntent; // If the user says we were wrong, what was the right answer?

    @Column(columnDefinition = "TEXT")
    private String userComments;
}