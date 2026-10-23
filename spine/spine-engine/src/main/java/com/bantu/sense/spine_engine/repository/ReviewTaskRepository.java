package com.bantu.sense.spine_engine.repository;

import com.bantu.sense.spine_engine.model.ReviewTask;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ReviewTaskRepository extends JpaRepository<ReviewTask, String> {
    List<ReviewTask> findAllByOrderBySampleIdAsc();
}
