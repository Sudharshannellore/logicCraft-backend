# Logicraft API

FastAPI + MongoDB backend for the Logicraft frontend (`../frontend`). It replaces every mock in
`frontend/src/mock`, `src/services` and the localStorage-backed Zustand stores with server-side state.
Response shapes match `frontend/src/types/index.ts` (camelCase JSON).

## Quick start

You need a MongoDB 7+ server. Either install [MongoDB Community Server](https://www.mongodb.com/try/download/community)
locally (it listens on `mongodb://localhost:27017`), or create a free [MongoDB Atlas](https://www.mongodb.com/atlas)
cluster and put its connection string in `MONGODB_URI` in `.env`.

```bash
cd backend
python -m venv .venv
.venv/Scripts/pip install -r requirements-dev.txt     # Windows; use .venv/bin/pip on macOS/Linux
cp .env.example .env
.venv/Scripts/python -m uvicorn app.main:app --port 8000
```

- Interactive docs: http://localhost:8000/docs
- On first start an empty database gets the catalog (problems, quests, plans; courses are live, not seeded). There is no demo data: every player comes from a real sign-up.
- `python -m app.seed` reloads catalog content after editing `app/seed/data` (it also drops the retired course collections); `python -m app.seed --reset` also deletes every player and their data.
- Tests: `.venv/Scripts/python -m pytest` (integration tests use a throwaway `codequest_test` database and skip themselves when MongoDB isn't running). Lint: `ruff check app tests`.

## Authentication

Players sign in with email and password. Every endpoint needs `Authorization: Bearer <accessToken>` except
`/health`, `/config/economy`, `/activity` (the landing page's feed) and `/auth/*`. In http://localhost:8000/docs,
click **Authorize** and enter an email (in the *username* box) and password.

| Endpoint | What it does |
|---|---|
| `POST /auth/register` `{username, email, password}` | Creates an account (200 starter XP) and signs it in |
| `POST /auth/login` `{email, password}` | Returns `{tokens, user}` |
| `POST /auth/refresh` `{refreshToken}` | Swaps a refresh token for a new pair; each refresh token works once |
| `POST /auth/logout` `{refreshToken}` | Ends this session |
| `POST /auth/logout-all` | Ends every session, including access tokens already issued |
| `POST /auth/change-password` `{currentPassword, newPassword}` | Signs out other devices and returns a new session |

How it works:
- **Passwords** are hashed with Argon2id. They need 8+ characters, including a letter and a number.
- **Access tokens** are JWTs that last `ACCESS_TOKEN_MINUTES` (default 30) and are signed with `JWT_SECRET`, which must be set in production.
- **Refresh tokens** are random and last `REFRESH_TOKEN_DAYS` (default 14). Only their SHA-256 is stored.
- **Revocation:** changing your password or signing out everywhere bumps a per-user token version, so existing access tokens stop working immediately.
- **Lockout:** after `LOGIN_MAX_FAILURES` wrong passwords, that email is locked for `LOGIN_LOCKOUT_MINUTES`.
- **Login errors** never say whether an email exists.

### Accounts

Create accounts through the sign-up page (or `POST /auth/register`). To test player-vs-player features
(friends, duels), sign up two accounts, for example in two browser profiles.

## Architecture

```
app/
├── main.py              app factory + lifespan (Mongo, HTTP client, executor, providers)
├── core/                config, errors → JSON, clock/ids, logging
├── db/                  Mongo client, collection names, indexes
├── schemas/             Pydantic models: snake_case in Mongo, camelCase on the wire
├── domain/              pure game rules, no I/O: levels/leagues, economy prices, mentor, resume AI, code review
├── repositories/        one class per collection; the only code that talks to MongoDB
├── integrations/        the outside world: tutorial platforms, code runners, SQL sandbox
├── services/            business logic: orchestrates repositories, domain rules and integrations
├── api/
│   ├── container.py     composition root: builds services lazily per request
│   ├── deps.py          `Services` and `CurrentUser` dependencies
│   └── routes/          thin routers: parse → one service call → response model
└── seed/                catalog fixtures (problems, quests, plans)
```

Dependencies point inward: `routes → services → repositories/integrations → schemas`, and `domain`
depends on nothing. Services never construct their own dependencies; `Container` wires them.

### Rules that keep state correct

- **XP is server-authoritative.** `xp` is spendable; `lifetime_xp` grows only on earned XP and drives
  level, league, rank and leaderboards. Spending is one atomic conditional update (`xp >= cost`), so a
  balance can never go negative. Every movement lands in the `xp_ledger` collection.
- **First-completion rewards pay once.** Rewards carry a key (`code:two-sum`, `lesson:py8`, `quest:2026-10-19`)
  backed by a unique index, so double-submits and retries can't pay twice.
- **Duels are compare-and-set.** Each transition (`pending → active → finished`) is conditional on the
  current status, and settlement is claimed once, so concurrent actions can't double-pay stakes.
- **Time-based state advances lazily on read**: duel timeouts, subscription drops,
  challenge clocks and rotations. There is no background worker to run.

## External tutorial platforms

All free. Results are fetched concurrently with per-provider timeouts, filtered for relevance, and cached
in Mongo (TTL index, 12 h by default). A failing provider is reported in `providers[]` and skipped; it
never fails the request.

| Provider | Used for | Key |
|---|---|---|
| DEV Community (dev.to) | articles | none |
| Stack Overflow (Stack Exchange API) | top-voted answered Q&A | optional `STACKEXCHANGE_KEY` (raises the quota from 300 to 10k requests/day) |
| MDN Web Docs | JavaScript references | none |
| Wikipedia REST | concept summaries | none (sends `HTTP_USER_AGENT`) |
| YouTube Data API v3 | videos | `YOUTUBE_API_KEY`; disabled without one |

- `GET /tutorials/search?q=closures&language=javascript` searches every platform.
- `GET /tutorials/reference?q=…` returns a one-paragraph explanation (MDN for JavaScript, otherwise Wikipedia).
- `GET /lessons/{id}/resources` returns live tutorials for a lesson's concept.
- If a lesson is ever missing from the database, the API assembles a stand-in from these references instead of failing.

To add a platform, subclass `TutorialProvider` in `app/integrations/tutorials/` and register it in `build_providers`.

## Courses

13 worlds, one per language: Python, JavaScript, SQL, TypeScript, Java, C#, C++, C, PHP, Go, Rust, Kotlin and
Swift. Every language in `app/domain/languages.py` gets a **live course** (`live-<language>`), built on demand from its Exercism track's `config.json`. Nothing is stored or seeded:

- **Map:** the track's concept exercises in prerequisite order, then practice exercises spread from easy to
  hard, up to 32 topics in zones of four, each guarded by a boss (the existing zone-boss challenges). Tracks
  with no syllabus (C, SQL) are taught through practice exercises alone. See `app/domain/live_courses.py`.
- **Lesson:** the concept doc as Markdown (`liveContent`, with its source link) and the exercise to solve
  (`exercise`), graded through the practice library endpoints where the language is gradable. There are no
  hand-written quizzes: the exercise's own tests are the check.
- **Freshness:** the syllabus is cached in Mongo for a day and the built course in memory for 5 minutes; if
  Exercism is down, the course list is empty until it's back.

To add a language, add one `LanguageInfo` line (with its Exercism track); its live course appears by itself.

### Framework courses

Beside the 13 language courses there are framework courses (`fw-<name>`, `kind: "framework"`): React, Next.js,
Svelte, Express, FastAPI, Laravel, Hugging Face Transformers, scikit-learn, pandas / data science and
generative AI. Each is built live from the project's own open-source docs on GitHub (MIT, Apache-2.0 or CC BY),
and each lesson credits its source and licence.

- **A framework is a recipe, not content.** `app/domain/docs_courses.py` holds one `DocsCourseSpec` per course: the
  repository, where the pages are, and how their order is known (a navigation file, numbered folders, or a short
  list). To add a framework, add one spec; the course appears by itself. `app/services/docs_courses.py` reads the
  repository, `app/domain/docs_markdown.py` turns MDX / MkDocs / VitePress pages into plain Markdown (callouts kept,
  components dropped, code never touched, images served from jsDelivr).
- **Same map and rules as a language course:** zones follow the docs' sections, with a boss per zone (the boss
  rounds are exercises in the framework's language) and XP per topic. Lessons have no graded exercise.
- **GitHub limits:** listing a repository uses GitHub's API (60 requests/hour without a token). Listings are cached
  for a day and the last good copy is kept for a month if GitHub can't be reached. Set `GITHUB_TOKEN` (any token
  with no scopes) for 5,000/hour.

### Framework practice and challenges

A framework can't be graded like a language's exercises (there is no React or FastAPI to run), so it is practised
and fought with **quizzes made from its own docs** (`app/domain/framework_quiz.py`, no AI): a sentence from a lesson
with one key term (`inline code` or **bold**) blanked out, and four options. The wrong options are other terms of
the same sort from the same material (a command among commands, a file among files); sentences that lean on unseen
text, labels and ambiguous sentences are skipped. The same page always gives the same questions.

- **Practice:** one quiz per lesson, untimed, retake any time. Pass at 70% to earn XP, once per lesson.
- **Daily quiz:** 5 questions across the framework, the same for everyone, 8 minutes, one run per UTC day, +100 XP.
- **Zone boss:** 6 questions on the zone's lessons, 12 minutes, retryable with fresh questions each run. Passing
  defeats the boss and opens the next zone. A zone with too little material is topped up from the rest of the
  framework; if there's still too little, the boss can be claimed without a fight and without XP.

Endpoints: `GET /frameworks`, `/frameworks/{course}/practice`, `/frameworks/{course}/challenges`,
`/quizzes/{id}` and `POST /quizzes/{id}/start | submit | claim`. Quiz ids: `fwq-practice-<lesson>`,
`fwq-daily-<yyyymmdd>-<course>`, `fwq-zone-<boss>`. Language courses are unchanged (Exercism exercises and bosses).

### Career paths

`GET /paths` lists industry routes (Full-Stack Web, Frontend, Backend (Node / Python / PHP), AI / ML, Data
Science, Systems, Enterprise, Mobile). Each is an ordered list of courses in `app/domain/career_paths.py`.

- A path's progress is read from its courses, so finishing a course anywhere counts in every path that contains it.
  Steps are `completed`, `in_progress`, `next` or `available`; nothing is locked, so learners can start any course.
- A path is suggested (`recommended`, with a `reason`) once the learner has finished or started a course in it:
  finish Python and the backend, AI and data paths come first.
- `PUT /paths/{id}/enroll` and `DELETE /paths/{id}/enroll` choose or leave a path (the only thing stored).

## Practice library (live exercises)

The Practice page draws on [Exercism](https://exercism.org)'s open-source (MIT) practice exercises:
about 1,400 across all 13 course languages, read live from each track's GitHub repository
(`raw.githubusercontent.com`, no API key) and cached in MongoDB. Track lists refresh daily and exercises
weekly, so new exercises appear on their own. Code: `app/integrations/exercism/` and `app/services/library.py`.

Each exercise is graded against **its own official test suite**, in the sandbox described below:

| Language | How the tests run here | Reference solutions passing |
|---|---|---|
| Python | the track's `unittest` file, by a small runner | 124 / 129 |
| JavaScript, TypeScript | the track's Jest spec, by a dependency-free Jest shim (`assets/jest.mjs`) on Node 24 | 121 / 130 · 103 / 108 |
| SQL (SQLite track) | the track's `sqlite3` shell scripts, replayed by `assets/sqlite_worker.py` | 74 / 81 |
| Java, C#, C++, C, PHP, Go, Rust, Kotlin, Swift | not here yet: the page shows the exercise and its tests, and links to Exercism's free online editor | — |

The exercises that fail with Exercism's own reference solution need things the sandbox blocks on
purpose (files, sockets, worker threads), run longer than the 20-second suite limit, or use the
`sqlite3` shell's `generate_series` (learners are told to use `WITH RECURSIVE`). A few are refactoring
exercises whose starter code already passes by design.

First solves pay XP by Exercism difficulty (levels 1–3: 60, 4–6: 120, 7–10: 200) and count toward
daily quests and stats. Endpoints: `GET /library/languages`, `GET /library/{language}/exercises`,
`GET /library/{language}/exercises/{slug}`, `POST …/run`, `POST …/submit`.

To grade another language here, add a runner in `app/integrations/exercism/runners.py` (its compiler and
test framework must be installed on the server) and add the language to `GRADED_HERE`.

## Live challenges

The Challenges page is built from the same Exercism tracks. Nothing is stored ahead of time: each challenge is
picked deterministically, so every player gets the same one. **A challenge is the same in every language**: it is
picked from the exercises that every language's track has (about 60, excluding SQL, whose track teaches a different
syllabus), and its id has no language (`daily-2026-10-20`). The player chooses the language they solve it in; the
clock, the fastest-times board and the bonus belong to the challenge, so switching language changes none of them.

| Challenge | Rotates | Exercises (Exercism level) | Clock | Bonus XP |
|---|---|---|---|---|
| Daily Challenge | 00:00 UTC | 1 (levels 3–5) | 30 min, one run | 100 |
| Speed Round | 00:00 UTC | 1 (levels 1–2) | 10 min, one run | 60 |
| Weekly Boss | Monday 00:00 UTC | 3 in order (1–3, 4–6, 7–10) | 60 min, retry from round 1 | 400 |
| Zone boss (course map) | never | the boss's rounds at the zone's level | 15 min per round, retry | the boss's reward; opens the next zone |

- **Picking.** Exercises in the level band are ordered by a hash of the challenge id and slug. Each candidate's
  starter code is test-run once in every language graded here (the verdict is cached for 14 days); an exercise
  whose starter doesn't run, or already passes, in any of them is skipped. Refactoring katas and "Hello, World!" are never picked.
  The pick is cached until the challenge rotates out. The first visit of the day can take a few seconds.
- **Timing is server-side.** `POST …/start` records the start and deadline in `challenge_attempts`; a stage
  only counts if it passes before the deadline. The solve time (start to final stage) goes on the
  fastest-times board, and the page shows real counts of players who started and won.
- **Rewards.** A submission is graded and recorded like a library solve (first solve pays the exercise's XP),
  plus the challenge bonus once per challenge (`challenge:{id}`). Wins count as `challenges_won`; the Weekly
  Boss and zone bosses add `bosses_defeated`; a Speed Round won in 2 minutes or less unlocks "Speed Coder".
- **Languages graded on Exercism** (Java, C#, C++, C, PHP, Go, Rust, Kotlin, Swift) show the same challenges
  with links to Exercism's editor, untimed and without a bonus. A zone boss in those courses can be claimed
  to open the next zone, but pays no XP because nothing is verified.

Endpoints: `GET /challenges?language=python`, `GET /challenges/{id}?language=`, `POST /challenges/{id}/start?language=`,
`POST /challenges/{id}/submit` (`{slug, language, files}`). `language` only chooses how the exercises are shown and
graded. Zone bosses: `GET /courses/{id}/bosses/{bossId}`,
`POST …/start`, `…/submit`, `…/claim`. Code: `app/domain/challenges.py`, `app/services/challenges.py`.

## Job board (live listings)

The Job Board shows real remote developer jobs, by course language, from two free job-board APIs. No
open-source job dataset exists; these are free public feeds that need no key.

| Board | API | Terms we follow |
|---|---|---|
| [Himalayas](https://himalayas.app/api) | `GET /jobs/api/search?q=…` (about 20 jobs a page, 2 pages) | Credit Himalayas with a visible link; Apply uses the `applicationLink`; don't pass listings on to other boards |
| [Jobicy](https://jobicy.com/jobs-rss-feed) | `GET /api/v2/remote-jobs?tag=…&count=50` (last 7 days) | Credit Jobicy with a link; Apply goes to the Jobicy listing; sync at most hourly |

- **Per language.** Each board is searched with the language's term (`app/domain/jobs.py`; Jobicy rejects
  terms under 3 characters and `#`, so C# is `.net` and Go is `golang`). Every job is then checked
  locally: it's listed under a language only if its title or description names it. Short names are matched
  carefully: "C" only in contexts like "C/C++" or "embedded C", "Go" never in "Go-to-market", and "SQL" never in "NoSQL".
- **Cached.** Listings are stored in `job_listings` and each board/language feed is fetched at most every 8
  hours (30 minutes after a failure). If a board is down, stored listings keep showing with a "may be a few
  hours old" note. A listing disappears 4 days after it was last seen, or when the board says it expires.
- **Normalised.** Board fields map onto Full-time / Part-time / Contract / Internship and Intern / Junior /
  Mid-level / Senior; HTML descriptions become Markdown; the same role posted once per country is listed once.
  Company logos are pixel art picked per company, since board logos are their trademarks.
- **Applying is free and happens on the board.** Quest AI can still tailor the resume (50 XP) and write a
  cover note (25 XP). *Apply* opens the board's page and records the application with what was prepared;
  the player sets its status (applied, interviewing, offer, rejected) as they hear back.

Endpoints: `GET /jobs?language=python` (optional `workMode`, `employment`, `level`, `q`), `GET /jobs/{id}`,
`POST /jobs/{id}/applications`, `GET /applications`, `PATCH /applications/{id}` (`{status}`).
Code: `app/integrations/jobs/`, `app/services/jobs.py`.

## Code execution

Code runs on this server in a locked-down child process: no containers and no external runner. Python uses
the server's interpreter; JavaScript needs Node.js 20+ on `PATH` (it's switched off with a warning otherwise).
`CODE_EXECUTOR=disabled` turns Run and Submit off.

Every run is confined in three layers (see [local.py](app/integrations/execution/local.py) and [harness.py](app/integrations/execution/harness.py)):

| Layer | Windows | Linux / macOS |
|---|---|---|
| OS limits | Job Object: memory cap, CPU-time cap, one process only. The child starts suspended and runs only once inside the job. | rlimits: address space (Python), CPU time, file size, open files, core dumps; own process group |
| Runtime guard, Python | Audit hook: no file reads outside the standard library, no writes, no subprocess/`os.system`/`fork`, no sockets, no ctypes | same |
| Runtime guard, JavaScript | Node `--permission`: no filesystem, child processes, workers or addons; the guard also removes network modules and `fetch` | same |
| Hygiene | Throwaway working directory, environment stripped to `PATH`/temp vars (the API's secrets never reach the child), low CPU priority, kill on timeout or output flood, at most `CODE_MAX_CONCURRENT` runs at once | same |

Limits are set in `.env`: `CODE_TIMEOUT_SECONDS`, `CODE_MEMORY_LIMIT_MB`, `CODE_MAX_OUTPUT_BYTES`, `CODE_MAX_CONCURRENT`.
`tests/unit/test_sandbox.py` holds the escape attempts this setup is checked against.

This stops what learners realistically try: reading the server's files and `.env`, network calls, shell commands,
fork bombs, memory bombs, infinite loops and output floods. It is not a VM-grade boundary. A determined attacker
with a Python or V8 exploit could get further, so run the API as a dedicated low-privilege OS user with no access
to anything it doesn't need.

Solutions are wrapped in a harness that calls the problem's entry function on every test case and compares
JSON results, so the learner's `print`s still show up as console output, and error messages point at the
learner's own line numbers. **Hidden test cases** run on Submit only. Expected outputs never reach the
child process, so a solution can't read or fake its way past them. C++ and Java have starter code but no
harness yet; Run/Submit tell the learner to switch language.

SQL runs against a fresh in-memory SQLite copy of the practice tables. An authorizer allows reads only and a
progress handler stops runaway queries. Answers are graded by **comparing result sets**, not by matching
query text; the old "required clause" fragments are only used as hints when a result is wrong.

## Frontend page → API map

All paths are under `/api/v1`.

| Page / store | Endpoints |
|---|---|
| Landing (activity ticker) | `GET /activity` |
| Dashboard | `GET /users/me`, `/wallet`, `/quests/daily`, `/courses`, `/leaderboard` |
| Learn, Course | `GET /courses`, `/courses/{id}`, `/courses/{id}/path` |
| Framework practice | `GET /frameworks`, `/frameworks/{course}/practice`, `/frameworks/{course}/challenges`; `/quizzes/{id}` (+ `start`, `submit`, `claim`) |
| Career paths | `GET /paths`, `/paths/{id}`; `PUT` / `DELETE /paths/{id}/enroll` |
| Lesson | `GET /lessons/{id}`, `/lessons/{id}/resources`, `POST /lessons/{id}/try-it`, `/quiz`, `/complete` |
| Practice library, exercise board | `GET /library/languages`, `/library/{language}/exercises[/{slug}]`, `POST …/run`, `…/submit` |
| Practice originals, Code board | `GET /problems`, `/problems/{slug}`, `POST /problems/{slug}/run`, `/submit` (optional `duelId`) |
| SQL sandbox, SQL problem | `GET /sql/tables`, `POST /sql/query`, `GET /sql/problems[/{slug}]`, `POST …/run`, `…/submit` |
| Challenges, challenge board, zone boss | `GET /challenges?language=`, `GET /challenges/{id}`, `POST …/start`, `…/submit`; `GET /courses/{id}/bosses/{bossId}`, `POST …/start`, `…/submit`, `…/claim` |
| Quests (+ streak rewards) | `GET /quests/daily`, `POST /quests/daily/claim`, `GET /rewards/streak-milestones`, `POST …/{days}/claim` |
| Achievements | `GET /achievements` |
| Leaderboard | `GET /leaderboard?scope=global\|weekly\|monthly\|friends` |
| Profile, Settings | `GET/PATCH /users/me`, `GET/PATCH /users/me/settings` |
| Friends (`socialStore`) | `GET /social`, `POST /social/friend-requests`, `…/{id}/accept`, `…/{id}/decline`, `DELETE /social/friend-requests/{id}`, `DELETE /social/friends/{id}` |
| Duels (`socialStore`) | `GET/POST /duels`, `POST /duels/{id}/accept`, `decline`, `cancel`, `start`, `forfeit` |
| Quest AI (`questAi.ts`) | `GET /mentor/intro`, `/mentor/suggestions`, `POST /mentor/ask` (10 XP) |
| Resume builder (`resumeStore`, `resumeAi.ts`) | `GET/POST /resumes`, `GET/PATCH/DELETE /resumes/{id}`, `PUT /resumes/{id}/data`, `POST …/activate`, `…/reset`, `GET /resume-templates`, `POST /resume-templates/{id}/unlock`, `POST /resume-ai/{bullet,summary,skills,tailor,cover-note,match}` |
| Job board (`applicationsStore`) | `GET /jobs?language=`, `/jobs/{id}`, `POST /jobs/{id}/applications`, `GET /applications`, `PATCH /applications/{id}` |
| Subscription (`subscriptionStore`) | `GET /store/plans`, `/store/packs`, `POST /store/packs/{id}/purchase`, `GET/POST /subscription`, `POST /subscription/cancel`, `/resume` |
| Wallet (`walletStore`) | `GET /wallet`, `/wallet/transactions`; every paid or rewarding action also returns the new `balance` |
| Prices shown in the UI | `GET /config/economy` |

## The frontend

`../frontend` is wired to this API. See its README for how the client handles sessions, XP and errors.
Timestamps (`appliedAt`, `updatedAt`, duel times, subscription dates) are epoch milliseconds.

## Known gaps

- **Achievement without a trigger.** "League Champion" has no rule yet, because there is no weekly-league flow.
- **Honour-system zone bosses** in the nine languages graded on Exercism: claiming one opens the next zone (no XP is paid).
- **Rule-based Quest AI.** The mentor and resume AI are rule-based ports of the frontend logic, behind service methods with the same signatures, ready to swap for an LLM.
- **Demo checkout.** Subscriptions and packs take no payment.
- **Remote jobs only.** Both job boards list remote roles; there's no free keyless feed of on-site jobs worldwide.
