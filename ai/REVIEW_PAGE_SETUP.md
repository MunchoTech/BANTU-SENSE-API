# Start the community review page

The reviewer page is at `/review`. It shows one phrase at a time, saves each answer to PostgreSQL, and does not show the answer key. The project-owner page is at `/review/results` and downloads the saved answers as a CSV.

## Before inviting reviewers

The task phrases are copied from the survey. Check that contributor consent allows sharing them with reviewers. Do not include the answer key in the website or give it to reviewers. Keep the owner download code private.

## Start it on this computer

The PostgreSQL database must be running, and the private blind review CSV must exist at `/tmp/bantu-sense-review/review_blind.csv`.

In one terminal, start the Spring API and load the phrases into the database:

```bash
cd ~/Documents/"My Projects"/Bantu-Sense-Core/spine/spine-engine
export BANTU_REVIEW_ACCESS_CODE='choose-a-long-private-review-code'
export BANTU_REVIEW_ADMIN_CODE='choose-a-different-owner-only-code'
export BANTU_REVIEW_TASKS_FILE='/tmp/bantu-sense-review/review_blind.csv'
./mvnw spring-boot:run
```

Choose your own codes and keep them out of project files. Give reviewers the access code and a different reviewer code for each person, such as `RVIEWER01`. Do not give them the owner code.

In another terminal, start the website:

```bash
cd ~/Documents/"My Projects"/Bantu-Sense-Core/bantu-sense-ui
VITE_API_BASE_URL='http://localhost:8080' npm run dev
```

Open `http://localhost:5173/review`. Reviewers enter the shared access code and their own reviewer code. They can return later with the same reviewer code and continue where they left off. Each reviewer code can submit one answer per phrase.

When answers are ready, open `http://localhost:5173/review/results`, enter the owner code, and download the response CSV. Keep that file and the separate answer key private.

The API loads phrases only when the review-task table is empty. Once loaded, the tasks remain in PostgreSQL if the temporary CSV is removed.

## Share it outside this computer

The `localhost` addresses above work only on the computer running the services. For people elsewhere to use the page, deploy the React site and Spring API to reachable HTTPS addresses. Set `VITE_API_BASE_URL` to the HTTPS API address when building the site, and set `BANTU_WEB_ORIGIN` to the exact HTTPS website address when starting Spring. Keep both access codes in the backend's private environment settings. Do not put secrets in frontend build settings or source files.

Do not share the page publicly until the contributor consent covers review by other people. Reviewer notes should not include names, phone numbers, or other personal details.
