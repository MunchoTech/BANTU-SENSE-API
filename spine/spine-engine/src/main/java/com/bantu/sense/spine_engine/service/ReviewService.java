package com.bantu.sense.spine_engine.service;

import com.bantu.sense.spine_engine.dto.ReviewQueueResponse;
import com.bantu.sense.spine_engine.dto.ReviewSubmissionRequest;
import com.bantu.sense.spine_engine.dto.ReviewTaskResponse;
import com.bantu.sense.spine_engine.model.ReviewSubmission;
import com.bantu.sense.spine_engine.model.ReviewTask;
import com.bantu.sense.spine_engine.repository.ReviewSubmissionRepository;
import com.bantu.sense.spine_engine.repository.ReviewTaskRepository;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.regex.Pattern;

@Service
public class ReviewService {
    private static final Pattern REVIEWER_CODE_PATTERN = Pattern.compile("[A-Za-z0-9_-]{2,24}");
    private static final Set<String> LANGUAGE_CHECKS = Set.of("correct", "incorrect", "unsure");
    private static final Set<String> INTENT_LABELS = Set.of("medical", "legal", "financial", "unclear");
    private static final Set<String> NATURALNESS_VALUES = Set.of("natural", "awkward", "unsure");

    private final ReviewTaskRepository taskRepository;
    private final ReviewSubmissionRepository submissionRepository;

    public ReviewService(ReviewTaskRepository taskRepository,
                         ReviewSubmissionRepository submissionRepository) {
        this.taskRepository = taskRepository;
        this.submissionRepository = submissionRepository;
    }

    @Transactional(readOnly = true)
    public ReviewQueueResponse getQueue(String reviewerCode) {
        String normalizedCode = validateReviewerCode(reviewerCode);
        List<ReviewTaskResponse> tasks = taskRepository.findAllByOrderBySampleIdAsc().stream()
                .map(task -> new ReviewTaskResponse(task.getSampleId(), task.getLanguage(), task.getPhrase()))
                .toList();
        List<String> completed = submissionRepository.findSampleIdsByReviewerCode(normalizedCode);
        return new ReviewQueueResponse(tasks, completed);
    }

    @Transactional
    public void submit(ReviewSubmissionRequest request) {
        if (request == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Review answers are required.");
        }
        String reviewerCode = validateReviewerCode(request.reviewerCode());
        String languageCheck = normalize(request.languageCheck());
        String intentLabel = normalize(request.intentLabel());
        String naturalness = normalize(request.naturalness());
        String notes = request.notes() == null ? "" : request.notes().trim();

        if (!LANGUAGE_CHECKS.contains(languageCheck)
                || !INTENT_LABELS.contains(intentLabel)
                || !NATURALNESS_VALUES.contains(naturalness)
                || notes.length() > 1000) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "One or more review answers are invalid.");
        }
        ReviewTask task = taskRepository.findById(request.sampleId() == null ? "" : request.sampleId().trim())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Review message not found."));
        if (submissionRepository.existsByTaskSampleIdAndReviewerCode(task.getSampleId(), reviewerCode)) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "You have already reviewed this message.");
        }

        ReviewSubmission submission = new ReviewSubmission();
        submission.setTask(task);
        submission.setReviewerCode(reviewerCode);
        submission.setLanguageCheck(languageCheck);
        submission.setIntentLabel(intentLabel);
        submission.setNaturalness(naturalness);
        submission.setNotes(notes.isBlank() ? null : notes);
        try {
            submissionRepository.saveAndFlush(submission);
        } catch (DataIntegrityViolationException exception) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "You have already reviewed this message.");
        }
    }

    @Transactional(readOnly = true)
    public String exportResultsCsv() {
        StringBuilder csv = new StringBuilder("sample_id,language,reviewer_code,language_check,intent_label,naturalness,notes,submitted_at\r\n");
        for (ReviewSubmission submission : submissionRepository.findAllByOrderByIdAsc()) {
            csv.append(csvField(submission.getTask().getSampleId())).append(',')
                    .append(csvField(submission.getTask().getLanguage())).append(',')
                    .append(csvField(submission.getReviewerCode())).append(',')
                    .append(csvField(submission.getLanguageCheck())).append(',')
                    .append(csvField(submission.getIntentLabel())).append(',')
                    .append(csvField(submission.getNaturalness())).append(',')
                    .append(csvField(submission.getNotes() == null ? "" : submission.getNotes())).append(',')
                    .append(csvField(submission.getSubmittedAt().toString())).append("\r\n");
        }
        return csv.toString();
    }

    private static String csvField(String value) {
        String escaped = value == null ? "" : value.replace("\"", "\"\"");
        return "\"" + escaped + "\"";
    }

    private static String validateReviewerCode(String code) {
        if (code == null || !REVIEWER_CODE_PATTERN.matcher(code.trim()).matches()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                    "Use the reviewer code given to you by the project owner (2–24 letters or numbers).");
        }
        return code.trim();
    }

    private static String normalize(String value) {
        return value == null ? "" : value.trim().toLowerCase(Locale.ROOT);
    }
}
