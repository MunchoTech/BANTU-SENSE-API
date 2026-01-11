package com.bantu.sense.spine_engine.repository;

import com.bantu.sense.spine_engine.model.Inquiry;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface InquiryRepository extends JpaRepository<Inquiry, Long> {
    // That's it! Spring now gives you .save(), .findAll(), .findById() for free.
}