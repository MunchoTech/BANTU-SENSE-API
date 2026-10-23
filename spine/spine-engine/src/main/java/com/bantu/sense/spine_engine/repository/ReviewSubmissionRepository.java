package com.bantu.sense.spine_engine.repository;

import com.bantu.sense.spine_engine.model.ReviewSubmission;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface ReviewSubmissionRepository extends JpaRepository<ReviewSubmission, Long> {
    boolean existsByTaskSampleIdAndReviewerCode(String sampleId, String reviewerCode);

    @Query("select submission.task.sampleId from ReviewSubmission submission where submission.reviewerCode = :reviewerCode")
    List<String> findSampleIdsByReviewerCode(@Param("reviewerCode") String reviewerCode);

    List<ReviewSubmission> findAllByOrderByIdAsc();
}
