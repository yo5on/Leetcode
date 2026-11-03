"""Update the README progress stats from a public LeetCode profile.

Needs no cookies: matchedUser is readable by anyone, like the profile page.
"""

import os
import re
import sys
import requests
from pathlib import Path


LEETCODE_URL = "https://leetcode.com/graphql/"

QUERY = """
query userProfile($username: String!) {
    matchedUser(username: $username) {
        username
        submitStats {
            acSubmissionNum {
                difficulty
                count
            }
        }
    }
}
"""

STATS_BLOCK = re.compile(
    r"(<!-- LEETCODE-STATS:START -->\n).*?(<!-- LEETCODE-STATS:END -->)",
    re.DOTALL,
)


def fetch_counts(username):
    """Return (canonical username, {"All": n, "Easy": n, "Medium": n, "Hard": n})."""

    response = requests.post(
        LEETCODE_URL,
        json={"operationName": "userProfile", "query": QUERY, "variables": {"username": username}},
        headers={"Content-Type": "application/json", "Referer": "https://leetcode.com/", "User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    response.raise_for_status()

    return parse_counts(response.json(), username)


def parse_counts(data, username):
    """Validate a matchedUser response so a bad one never overwrites the README."""

    user = (data.get("data") or {}).get("matchedUser")

    if not user:
        errors = "; ".join(e.get("message", "") for e in data.get("errors") or [])
        raise ValueError(f"LeetCode returned no profile for '{username}'. {errors}".strip())

    counts = {item["difficulty"]: item["count"] for item in user["submitStats"]["acSubmissionNum"]}

    for name in ("All", "Easy", "Medium", "Hard"):
        if not isinstance(counts.get(name), int):
            raise ValueError(f"LeetCode response is missing the {name} count: {counts}")

    return user["username"], counts


def render_stats(readme, counts, username):
    """Return readme with the stats block replaced by username's profile and counts."""

    lines = [f"- <samp>Profile: [{username}](https://leetcode.com/u/{username}/)</samp>"]
    lines += [f"- <samp>Total Solved: {counts['All']}</samp>"]
    lines += [f"- <samp>{name}: {counts[name]}</samp>" for name in ("Easy", "Medium", "Hard")]

    if not STATS_BLOCK.search(readme):
        raise ValueError("README.md is missing the LEETCODE-STATS markers.")

    return STATS_BLOCK.sub(lambda m: m[1] + "\n".join(lines) + "\n" + m[2], readme)


def _self_test():

    response = {"data": {"matchedUser": {"username": "Someone", "submitStats": {"acSubmissionNum": [
        {"difficulty": "All", "count": 4}, {"difficulty": "Easy", "count": 2},
        {"difficulty": "Medium", "count": 1}, {"difficulty": "Hard", "count": 1}]}}}}
    username, counts = parse_counts(response, "someone")
    assert username == "Someone" and counts == {"All": 4, "Easy": 2, "Medium": 1, "Hard": 1}

    bad_responses = [
        {"errors": [{"message": "That user does not exist."}], "data": {"matchedUser": None}},
        {"data": None},
        {"data": {"matchedUser": {"username": "x", "submitStats": {"acSubmissionNum": [{"difficulty": "All", "count": 1}]}}}},
    ]
    for bad in bad_responses:
        try:
            parse_counts(bad, "x")
        except ValueError:
            continue
        raise AssertionError(f"accepted bad response {bad!r}")

    readme = "a\n<!-- LEETCODE-STATS:START -->\nold\n<!-- LEETCODE-STATS:END -->\nb"
    updated = render_stats(readme, counts, username)
    assert "[Someone](https://leetcode.com/u/Someone/)" in updated
    assert updated.startswith("a\n<!-- LEETCODE-STATS:START -->") and updated.endswith("<!-- LEETCODE-STATS:END -->\nb")
    assert "Total Solved: 4" in updated and "Easy: 2" in updated and "Medium: 1" in updated and "Hard: 1" in updated
    assert "old" not in updated

    try:
        render_stats("no markers", counts, username)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted README without markers")

    print("Self-test passed.")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _self_test()
        sys.exit(0)

    requested = os.environ.get("LEETCODE_USERNAME", "").strip()

    if not requested:
        sys.exit("Set LEETCODE_USERNAME to your LeetCode username.")

    username, counts = fetch_counts(requested)
    readme_path = Path("README.md")
    readme_path.write_text(render_stats(readme_path.read_text(encoding="utf-8"), counts, username), encoding="utf-8")
    print(f"Updated README.md for {username}: {counts}")
