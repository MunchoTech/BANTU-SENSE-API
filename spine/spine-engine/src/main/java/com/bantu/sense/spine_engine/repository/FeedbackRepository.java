package com.bantu.sense.spine_engine.repository;



import com.bantu.sense.spine_engine.model.Feedback;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface FeedbackRepository extends JpaRepository<Feedback, Long> {
    // You can now save user corrections to improve your AI later.
}