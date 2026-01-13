package com.bantu.sense.spine_engine.model;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

import java.time.LocalDateTime;

@Entity
@Table(name = "users")
@Data
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private long id;

    @Column(unique=true, nullable = false)
    private String phoneNumber;
    private String firstName;
    private String lastName;
    private String preferredLanguage;
    private String province;

    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate(){
        createdAt = LocalDateTime.now();
    }


}
