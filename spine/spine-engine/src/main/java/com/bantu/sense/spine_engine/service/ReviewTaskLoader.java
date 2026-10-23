package com.bantu.sense.spine_engine.service;

import com.bantu.sense.spine_engine.model.ReviewTask;
import com.bantu.sense.spine_engine.repository.ReviewTaskRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

@Component
public class ReviewTaskLoader implements ApplicationRunner {
    private final ReviewTaskRepository taskRepository;
    private final String sourceFile;

    public ReviewTaskLoader(ReviewTaskRepository taskRepository,
                            @Value("${bantu.review.tasks-file:}") String sourceFile) {
        this.taskRepository = taskRepository;
        this.sourceFile = sourceFile;
    }

    @Override
    public void run(ApplicationArguments args) throws IOException {
        if (sourceFile.isBlank() || taskRepository.count() > 0) {
            return;
        }
        Path path = Path.of(sourceFile).toAbsolutePath().normalize();
        if (!Files.isRegularFile(path)) {
            throw new IllegalStateException("Review task CSV does not exist: " + path);
        }

        List<List<String>> rows = parseCsv(Files.readString(path, StandardCharsets.UTF_8));
        if (rows.isEmpty()) {
            throw new IllegalStateException("Review task CSV is empty.");
        }
        List<String> header = rows.get(0);
        int idColumn = header.indexOf("sample_id");
        int languageColumn = header.indexOf("language");
        int phraseColumn = header.indexOf("phrase");
        if (idColumn < 0 || languageColumn < 0 || phraseColumn < 0) {
            throw new IllegalStateException("Review task CSV must have sample_id, language, and phrase columns.");
        }

        List<ReviewTask> tasks = new ArrayList<>();
        for (int rowIndex = 1; rowIndex < rows.size(); rowIndex++) {
            List<String> row = rows.get(rowIndex);
            if (row.size() <= Math.max(idColumn, Math.max(languageColumn, phraseColumn))) {
                continue;
            }
            String sampleId = row.get(idColumn).trim();
            String language = row.get(languageColumn).trim().toLowerCase();
            String phrase = row.get(phraseColumn).trim();
            if (sampleId.isBlank() || phrase.isBlank()
                    || !(language.equals("bemba") || language.equals("nyanja"))) {
                throw new IllegalStateException("Review task CSV contains an invalid task at row " + (rowIndex + 1));
            }
            ReviewTask task = new ReviewTask();
            task.setSampleId(sampleId);
            task.setLanguage(language);
            task.setPhrase(phrase);
            tasks.add(task);
        }
        taskRepository.saveAll(tasks);
        System.out.printf("Loaded %d blind language review tasks.%n", tasks.size());
    }

    private static List<List<String>> parseCsv(String content) {
        List<List<String>> rows = new ArrayList<>();
        List<String> row = new ArrayList<>();
        StringBuilder field = new StringBuilder();
        boolean quoted = false;
        for (int i = 0; i < content.length(); i++) {
            char current = content.charAt(i);
            if (quoted) {
                if (current == '"') {
                    if (i + 1 < content.length() && content.charAt(i + 1) == '"') {
                        field.append('"');
                        i++;
                    } else {
                        quoted = false;
                    }
                } else {
                    field.append(current);
                }
            } else if (current == '"' && field.isEmpty()) {
                quoted = true;
            } else if (current == ',') {
                row.add(field.toString());
                field.setLength(0);
            } else if (current == '\n' || current == '\r') {
                if (current == '\r' && i + 1 < content.length() && content.charAt(i + 1) == '\n') {
                    i++;
                }
                row.add(field.toString());
                field.setLength(0);
                if (!(row.size() == 1 && row.get(0).isEmpty())) {
                    rows.add(row);
                }
                row = new ArrayList<>();
            } else {
                field.append(current);
            }
        }
        if (quoted) {
            throw new IllegalStateException("Review task CSV contains an unfinished quoted field.");
        }
        if (!row.isEmpty() || !field.isEmpty()) {
            row.add(field.toString());
            rows.add(row);
        }
        if (!rows.isEmpty() && rows.get(0).get(0).startsWith("\uFEFF")) {
            rows.get(0).set(0, rows.get(0).get(0).substring(1));
        }
        return rows;
    }
}
