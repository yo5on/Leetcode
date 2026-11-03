import base64
import json
import os
import re
import sys
import time
import requests
from datetime import datetime, timezone
from pathlib import Path


# ============================================================
# SESSION COOKIE EXPIRY
# ============================================================

def session_expiry(token):
    """Unix expiry time of a LEETCODE_SESSION JWT, or None if it has none.

    Raises ValueError when the value is not a JWT at all.
    """

    if not re.fullmatch(r"[\w-]+\.[\w-]+\.[\w-]+", token):
        raise ValueError(
            "LEETCODE_SESSION is not a valid cookie value. Check for quotes, "
            "a 'LEETCODE_SESSION=' prefix, or a truncated copy."
        )

    payload = token.split(".")[1]

    try:
        claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    except ValueError:
        # Raised without the original error, which can quote bytes of the cookie.
        raise ValueError("LEETCODE_SESSION payload could not be decoded.") from None

    if not isinstance(claims, dict):
        return None

    if "exp" in claims:
        return int(claims["exp"])

    # LeetCode sessions expire _session_expiry seconds (14 days) after refreshed_at.
    if "refreshed_at" in claims and "_session_expiry" in claims:
        return int(claims["refreshed_at"]) + int(claims["_session_expiry"])

    return None


# ============================================================
# README PROGRESS STATS
# ============================================================

STATS_BLOCK = re.compile(
    r"(<!-- LEETCODE-STATS:START -->\n).*?(<!-- LEETCODE-STATS:END -->)",
    re.DOTALL,
)


def render_stats(readme, solved_problems, username):
    """Return readme with the stats block replaced by username's profile and counts."""

    counts = {"Easy": 0, "Medium": 0, "Hard": 0}

    for problem in solved_problems:
        difficulty = problem["difficulty"].capitalize()
        counts[difficulty] = counts.get(difficulty, 0) + 1

    lines = [f"- <samp>Profile: [{username}](https://leetcode.com/u/{username}/)</samp>"]
    lines += [f"- <samp>Total Solved: {len(solved_problems)}</samp>"]
    lines += [f"- <samp>{name}: {counts[name]}</samp>" for name in ("Easy", "Medium", "Hard")]

    if not STATS_BLOCK.search(readme):
        raise ValueError("README.md is missing the LEETCODE-STATS markers.")

    return STATS_BLOCK.sub(lambda m: m[1] + "\n".join(lines) + "\n" + m[2], readme)


# ============================================================
# STALE SOLUTION PRUNING
# ============================================================

SOLUTION_FOLDER = re.compile(r"\d{4}-.+")


def prune_stale_solutions(keep_folders, root=Path(".")):
    """Delete solution.* files in problem folders not in keep_folders.

    keep_folders holds paths like Path("Easy", "0001-Two-Sum"), relative to root.
    Only solution.* files inside NNNN-Title folders are touched, so other files
    stay. Returns the deleted paths.
    """

    removed = []

    for difficulty in ("Easy", "Medium", "Hard"):
        base = root / difficulty

        if not base.is_dir():
            continue

        for folder in base.iterdir():
            if (
                not folder.is_dir()
                or not SOLUTION_FOLDER.fullmatch(folder.name)
                or folder.relative_to(root) in keep_folders
            ):
                continue

            for file in folder.glob("solution.*"):
                file.unlink()
                removed.append(file)

            if not any(folder.iterdir()):
                folder.rmdir()

    return removed


def _self_test():

    def jwt(claims):
        body = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
        return f"eyJhbGciOiJIUzI1NiJ9.{body}.sig"

    assert session_expiry(jwt({"refreshed_at": 1000, "_session_expiry": 1209600})) == 1210600
    assert session_expiry(jwt({"exp": 42})) == 42
    assert session_expiry(jwt({"username": "x"})) is None

    for bad in ('"a.b.c"', "LEETCODE_SESSION=a.b.c", "a.b", "", "a.!!.c", "a.bm90LWpzb24.c"):
        try:
            session_expiry(bad)
        except ValueError:
            continue
        raise AssertionError(f"accepted malformed value {bad!r}")

    readme = "a\n<!-- LEETCODE-STATS:START -->\nold\n<!-- LEETCODE-STATS:END -->\nb"
    updated = render_stats(readme, [{"difficulty": d} for d in ("EASY", "EASY", "MEDIUM", "HARD")], "someone")
    assert "[someone](https://leetcode.com/u/someone/)" in updated
    assert updated.startswith("a\n<!-- LEETCODE-STATS:START -->") and updated.endswith("<!-- LEETCODE-STATS:END -->\nb")
    assert "Total Solved: 4" in updated and "Easy: 2" in updated and "Medium: 1" in updated and "Hard: 1" in updated
    assert "old" not in updated

    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        files = {
            "Easy/0001-A/solution.py": "keep",
            "Easy/0002-B/solution.c": "stale",
            "Easy/0002-B/notes.md": "personal",
            "Medium/0003-C/solution.java": "stale",
            "Hard/notes/solution.py": "personal",
        }
        for name, text in files.items():
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text(text)

        removed = prune_stale_solutions({Path("Easy", "0001-A")}, root)

        assert sorted(p.relative_to(root).as_posix() for p in removed) == [
            "Easy/0002-B/solution.c", "Medium/0003-C/solution.java"]
        assert (root / "Easy/0001-A/solution.py").exists()
        assert (root / "Easy/0002-B/notes.md").exists()
        assert not (root / "Medium/0003-C").exists()
        assert (root / "Hard/notes/solution.py").exists()

    print("Self-test passed.")


if "--self-test" in sys.argv:
    _self_test()
    sys.exit(0)


# ============================================================
# CONFIGURATION
# ============================================================

LEETCODE_URL = "https://leetcode.com/graphql/"

SESSION = os.environ["LEETCODE_SESSION"].strip()
CSRF = os.environ["LEETCODE_CSRF_TOKEN"].strip()
EXPECTED_USERNAME = os.environ.get("LEETCODE_USERNAME", "").strip()

cookies = {
    "LEETCODE_SESSION": SESSION,
    "csrftoken": CSRF,
}

headers = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com/progress/",
    "Origin": "https://leetcode.com",
    "User-Agent": "Mozilla/5.0",
    "x-csrftoken": CSRF,
}


# ============================================================
# GRAPHQL HELPER
# ============================================================

def graphql(query, variables, operation_name):

    response = requests.post(
        LEETCODE_URL,
        json={
            "operationName": operation_name,
            "query": query,
            "variables": variables,
        },
        headers=headers,
        cookies=cookies,
        timeout=30,
    )

    if response.status_code != 200:
        print("LeetCode HTTP response:", response.text)
        response.raise_for_status()

    data = response.json()

    if "errors" in data:
        raise Exception(f"LeetCode GraphQL errors: {data['errors']}")

    if not data.get("data"):
        raise Exception(f"LeetCode returned no data: {data}")

    return data["data"]


# ============================================================
# VERIFY LOGIN
# ============================================================

def verify_login():

    # Only the expiry date is printed; the cookie and its other claims stay private.
    expiry = session_expiry(SESSION)

    if expiry is None:
        print("::warning::Could not read the LEETCODE_SESSION expiry date.")
    else:
        expires_at = datetime.fromtimestamp(expiry, timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        days_left = (expiry - time.time()) / 86400

        if days_left <= 0:
            print(f"::warning::LEETCODE_SESSION expired on {expires_at}.")
        elif days_left < 3:
            print(
                f"::warning::LEETCODE_SESSION expires {expires_at} "
                f"({days_left:.1f} days left). Refresh both secrets soon."
            )
        else:
            print(f"LEETCODE_SESSION valid until {expires_at} ({days_left:.0f} days left).")

    query = """
    query userStatus {
        userStatus {
            isSignedIn
            username
        }
    }
    """

    result = graphql(query, {}, "userStatus")
    status = result.get("userStatus")

    if not status or not status.get("isSignedIn"):
        if expiry is not None and expiry <= time.time():
            reason = f"LEETCODE_SESSION expired on {expires_at}."
        else:
            reason = (
                "LEETCODE_SESSION was rejected before its expiry date, usually "
                "because you logged out of the browser it was copied from."
            )
        raise Exception(
            f"LeetCode authentication failed. {reason} "
            "Sign in to leetcode.com and update LEETCODE_SESSION and "
            "LEETCODE_CSRF_TOKEN with fresh cookie values."
        )

    username = (status.get("username") or "").strip()

    if EXPECTED_USERNAME and username.lower() != EXPECTED_USERNAME.lower():
        raise Exception(
            f"Authenticated as '{username}', but LEETCODE_USERNAME is "
            f"'{EXPECTED_USERNAME}'. Refusing to sync the wrong account."
        )

    print(f"Authenticated as: {username}")

    return username


# ============================================================
# GET ALL SOLVED PROBLEMS
# ============================================================

def get_all_solved_problems():

    query = """
    query userProgressQuestionList(
        $filters: UserProgressQuestionListInput
    ) {
        userProgressQuestionList(filters: $filters) {
            totalNum
            questions {
                frontendId
                title
                titleSlug
                difficulty
                lastSubmittedAt
            }
        }
    }
    """

    all_questions = []
    skip = 0
    limit = 100

    while True:

        print(
            f"Fetching solved problems "
            f"(starting at {skip})..."
        )

        result = graphql(
            query,
            {
                "filters": {
                    "questionStatus": "SOLVED",
                    "skip": skip,
                    "limit": limit,
                }
            },
            "userProgressQuestionList",
        )

        progress = result.get("userProgressQuestionList")

        if progress is None:
            raise Exception(
                "LeetCode returned null for userProgressQuestionList. "
                "Authentication succeeded, but this progress endpoint "
                "did not return a result."
            )

        questions = progress.get("questions") or []
        all_questions.extend(questions)

        total = progress.get("totalNum", len(all_questions))

        print(
            f"Found {len(all_questions)} / {total} solved problems"
        )

        if len(all_questions) >= total:
            break

        if not questions:
            break

        skip += limit

        # Avoid hammering LeetCode
        time.sleep(1)

    return all_questions


# ============================================================
# GET SUBMISSIONS FOR A PROBLEM
# ============================================================

def get_submissions(title_slug):

    query = """
    query submissionList(
        $offset: Int!,
        $limit: Int!,
        $questionSlug: String!
    ) {
        questionSubmissionList(
            offset: $offset,
            limit: $limit,
            questionSlug: $questionSlug
        ) {
            submissions {
                id
                statusDisplay
                lang
                timestamp
            }
        }
    }
    """

    submissions = []
    offset = 0
    limit = 20

    while True:
        result = graphql(
            query,
            {
                "offset": offset,
                "limit": limit,
                "questionSlug": title_slug,
            },
            "submissionList",
        )

        submission_list = result.get("questionSubmissionList")

        if not submission_list:
            break

        page = submission_list.get("submissions") or []
        submissions.extend(page)

        if len(page) < limit:
            break

        offset += limit
        time.sleep(0.5)

    return submissions


# ============================================================
# GET ACTUAL SOURCE CODE
# ============================================================

def get_submission_details(submission_id):

    query = """
    query submissionDetails($submissionId: Int!) {
        submissionDetails(submissionId: $submissionId) {
            code
            lang {
                name
            }
            statusDisplay
        }
    }
    """

    result = graphql(
        query,
        {
            "submissionId": int(submission_id),
        },
        "submissionDetails",
    )

    return result.get("submissionDetails")


# ============================================================
# LANGUAGE → FILE EXTENSION
# ============================================================

LANG_EXTENSIONS = {
    "python": "py",
    "python3": "py",
    "java": "java",
    "c": "c",
    "cpp": "cpp",
    "c++": "cpp",
    "javascript": "js",
    "typescript": "ts",
    "kotlin": "kt",
    "go": "go",
    "rust": "rs",
    "swift": "swift",
    "csharp": "cs",
    "c#": "cs",
    "ruby": "rb",
    "php": "php",
    "scala": "scala",
    "dart": "dart",
    "sql": "sql",
}


# ============================================================
# CLEAN FILE/FOLDER NAMES
# ============================================================

def clean_name(name):

    name = re.sub(
        r'[<>:"/\\|?*]',
        "",
        name
    )

    name = name.strip()

    return name.replace(" ", "-")


def problem_folder(problem):

    number = str(problem["frontendId"]).zfill(4)

    return Path(
        problem["difficulty"].capitalize(),
        f"{number}-{clean_name(problem['title'])}"
    )


# ============================================================
# FIND LATEST ACCEPTED SUBMISSION
# ============================================================

def get_latest_accepted_submission(title_slug):

    submissions = get_submissions(title_slug)

    accepted = [
        submission
        for submission in submissions
        if submission.get("statusDisplay") == "Accepted"
    ]

    if not accepted:
        return None

    accepted.sort(
        key=lambda x: int(x.get("timestamp", 0)),
        reverse=True
    )

    return accepted[0]


# ============================================================
# MAIN SYNC
# ============================================================

print("=" * 60)
print("        LEETCODE → GITHUB SYNC")
print("=" * 60)

try:
    username = verify_login()
    solved_problems = get_all_solved_problems()

except Exception as error:
    print("ERROR while getting solved problems:")
    print(error)
    raise


print()
print(
    f"Total solved problems found: "
    f"{len(solved_problems)}"
)

readme_path = Path("README.md")
readme_path.write_text(
    render_stats(readme_path.read_text(encoding="utf-8"), solved_problems, username),
    encoding="utf-8"
)
print("Updated LeetCode progress in README.md")

# An empty list more likely means a bad response than a brand-new account,
# so never let it wipe the repository.
if solved_problems:
    for path in prune_stale_solutions({problem_folder(p) for p in solved_problems}):
        print(f"  ✗ Removed unsolved → {path}")
else:
    print("::warning::No solved problems returned; skipped removing stale solutions.")

print()


# ============================================================
# PROCESS EVERY SOLVED PROBLEM
# ============================================================

# A solved problem with no accepted submission or details usually means the
# session dropped or LeetCode rate-limited us, so those count as failures too.
failed = []

for index, problem in enumerate(
    solved_problems,
    start=1
):

    title = problem["title"]
    slug = problem["titleSlug"]
    difficulty = problem["difficulty"].capitalize()

    try:

        print(
            f"[{index}/{len(solved_problems)}] "
            f"{difficulty} - {title}"
        )

        submission = get_latest_accepted_submission(slug)

        if not submission:
            print("  ✗ No accepted submission found")
            failed.append(title)
            continue

        details = get_submission_details(submission["id"])

        if not details:
            print("  ✗ Could not get submission details")
            failed.append(title)
            continue

        if details["statusDisplay"] != "Accepted":
            print("  ⚠ Submission is not accepted")
            continue

        code = details["code"]
        language = details["lang"]["name"]

        extension = LANG_EXTENSIONS.get(language.lower())

        if not extension:
            print(f"  ⚠ Unsupported language: {language}")
            continue

        folder = problem_folder(problem)

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        solution_file = folder / f"solution.{extension}"

        # Keep only the latest accepted language for each problem.
        for old in folder.glob("solution.*"):
            if old != solution_file:
                old.unlink()
                print(f"  ✗ Removed old language → {old}")

        solution_file.write_text(
            code,
            encoding="utf-8"
        )

        print(
            f"  ✓ Synced → "
            f"{folder}/solution.{extension}"
        )

        time.sleep(1)

    except Exception as error:
        print(
            f"  ✗ Error processing "
            f"{title}: {error}"
        )
        failed.append(title)
        continue


print()
print("=" * 60)

if failed:
    print(f"   SYNC FINISHED WITH {len(failed)} FAILED PROBLEM(S)")
    print("=" * 60)
    print("Failed: " + ", ".join(failed))
    sys.exit(1)

print("           SYNC COMPLETED")
print("=" * 60)
