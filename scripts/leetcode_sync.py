import os
import re
import time
import requests
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

LEETCODE_URL = "https://leetcode.com/graphql/"

SESSION = os.environ["LEETCODE_SESSION"]
CSRF = os.environ["LEETCODE_CSRF_TOKEN"]

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
        raise Exception(
            "LeetCode authentication failed. "
            "LEETCODE_SESSION or LEETCODE_CSRF_TOKEN may be expired."
        )

    print(f"Authenticated as: {status.get('username')}")


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

    result = graphql(
        query,
        {
            "offset": 0,
            "limit": 20,
            "questionSlug": title_slug,
        },
        "submissionList",
    )

    submission_list = result.get("questionSubmissionList")

    if not submission_list:
        return []

    return submission_list.get("submissions") or []


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


# ============================================================
# FIND LATEST ACCEPTED SUBMISSION
# ============================================================

def get_latest_accepted_submission(title_slug):

    submissions = get_submissions(title_slug)

    accepted = [
        submission
        for submission in submissions
        if submission["statusDisplay"] == "Accepted"
    ]

    if not accepted:
        return None

    accepted.sort(
        key=lambda x: int(x["timestamp"]),
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
    verify_login()
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
print()


# ============================================================
# PROCESS EVERY SOLVED PROBLEM
# ============================================================

for index, problem in enumerate(
    solved_problems,
    start=1
):

    title = problem["title"]
    slug = problem["titleSlug"]
    difficulty = problem["difficulty"]

    try:

        print(
            f"[{index}/{len(solved_problems)}] "
            f"{difficulty} - {title}"
        )

        submission = get_latest_accepted_submission(slug)

        if not submission:
            print("  ⚠ No accepted submission found")
            continue

        details = get_submission_details(submission["id"])

        if not details:
            print("  ⚠ Could not get submission details")
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

        number = str(problem["frontendId"]).zfill(4)
        clean_title = clean_name(title)

        folder = Path(
            difficulty,
            f"{number}-{clean_title}"
        )

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        solution_file = folder / f"solution.{extension}"

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
        continue


print()
print("=" * 60)
print("           SYNC COMPLETED")
print("=" * 60)
