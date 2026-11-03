"""Update the README progress card from a public LeetCode profile.

Needs no cookies: matchedUser and allQuestionsCount are readable by anyone,
like the profile page. Writes an SVG card next to the README, because GitHub
strips inline SVG from Markdown.
"""

import os
import re
import sys
import tempfile
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr


LEETCODE_URL = "https://leetcode.com/graphql/"

QUERY = """
query userProfile($username: String!) {
    allQuestionsCount {
        difficulty
        count
    }
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

SVG_PATH = "assets/leetcode-stats.svg"

DIFFICULTIES = ("Easy", "Medium", "Hard")
COLORS = {"Easy": "#00b8a3", "Medium": "#ffb020", "Hard": "#ff375f", "All": "#58a6ff"}

STATS_BLOCK = re.compile(
    r"(<!-- LEETCODE-STATS:START -->\n).*?(<!-- LEETCODE-STATS:END -->)",
    re.DOTALL,
)


def fetch_profile(username):
    """Return the raw public GraphQL response for username."""

    response = requests.post(
        LEETCODE_URL,
        json={"operationName": "userProfile", "query": QUERY, "variables": {"username": username}},
        headers={"Content-Type": "application/json", "Referer": "https://leetcode.com/", "User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    response.raise_for_status()

    return response.json()


def parse_counts(data, username):
    """Return (canonical username, solved counts, question totals), each {"All": n, "Easy": n, ...}.

    Validates the response so a bad one never overwrites the README.
    """

    user = (data.get("data") or {}).get("matchedUser")

    if not user:
        errors = "; ".join(e.get("message", "") for e in data.get("errors") or [])
        raise ValueError(f"LeetCode returned no profile for '{username}'. {errors}".strip())

    counts = _by_difficulty(user["submitStats"]["acSubmissionNum"], "solved")
    totals = _by_difficulty(data["data"].get("allQuestionsCount") or [], "question total")

    return user["username"], counts, totals


def _by_difficulty(items, what):

    found = {item["difficulty"]: item["count"] for item in items}

    for name in ("All",) + DIFFICULTIES:
        if not isinstance(found.get(name), int) or found[name] < 0:
            raise ValueError(f"LeetCode response is missing the {name} {what} count: {found}")

    return found


def fraction(solved, total):
    """Solved share in [0, 1]; 0 when LeetCode reports no questions."""

    return min(solved / total, 1.0) if total > 0 else 0.0


def percent_label(solved, total):
    """One decimal below 10% so a few solves don't read as 0%."""

    if total <= 0:
        return "–"
    pct = fraction(solved, total) * 100
    if 0 < pct < 0.05:
        return "<0.1%"
    return f"{pct:.1f}%" if 0 < pct < 10 else f"{pct:.0f}%"


def bar_width(solved, total, width, height):
    """Filled length of a progress bar; any solve stays visible as at least a dot."""

    filled = fraction(solved, total) * width
    return max(filled, height) if solved > 0 and total > 0 else filled


def alt_text(counts, totals, username):

    parts = ", ".join(f"{name} {counts[name]} of {totals[name]}" for name in DIFFICULTIES)
    return f"LeetCode progress for {username}: {counts['All']} solved ({parts})"


def render_svg(counts, totals, username):
    """Return a self-contained 600x300 SVG progress card (no scripts, fonts or external refs)."""

    font = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300" viewBox="0 0 600 300" '
        f'role="img" aria-labelledby="title"><title id="title">{escape(alt_text(counts, totals, username))}</title>',
        '<rect x="0.5" y="0.5" width="599" height="299" rx="14" fill="#0d1b2a" stroke="#30363d"/>',
        f'<g font-family="{font}">',
        '<text x="28" y="44" fill="#8b949e" font-size="13" font-weight="600" letter-spacing="1.5">LEETCODE PROGRESS</text>',
        f'<text x="28" y="66" fill="#c9d1d9" font-size="14">@{escape(username)}</text>',
        f'<text x="28" y="122" fill="#ffffff" font-size="48" font-weight="700">{counts["All"]}</text>',
        f'<text x="28" y="146" fill="#8b949e" font-size="14">Total Solved · of {totals["All"]:,} problems</text>',
    ]

    # Overall ring, top right.
    ring = 2 * 3.14159265 * 36
    arc = fraction(counts["All"], totals["All"]) * ring
    out.append('<circle cx="530" cy="88" r="36" fill="none" stroke="#21262d" stroke-width="8"/>')
    if arc > 0:
        out.append(
            f'<circle cx="530" cy="88" r="36" fill="none" stroke="{COLORS["All"]}" stroke-width="8" '
            f'stroke-linecap="round" stroke-dasharray="{arc:.2f} {ring:.2f}" transform="rotate(-90 530 88)"/>'
        )
    out.append(
        '<text x="530" y="93" fill="#ffffff" font-size="14" font-weight="600" text-anchor="middle">'
        f'{escape(percent_label(counts["All"], totals["All"]))}</text>'
    )

    card_w, gap, bar_w, bar_h = 172, 14, 140, 8
    for i, name in enumerate(DIFFICULTIES):
        x = 28 + i * (card_w + gap)
        solved, total, color = counts[name], totals[name], COLORS[name]
        fill = bar_width(solved, total, bar_w, bar_h)
        out += [
            f'<rect x="{x}" y="170" width="{card_w}" height="104" rx="10" fill="#161b22" stroke="#30363d"/>',
            f'<text x="{x + 16}" y="196" fill="{color}" font-size="14" font-weight="600">{name}</text>',
            f'<text x="{x + card_w - 16}" y="196" fill="#8b949e" font-size="13" text-anchor="end">'
            f'{escape(percent_label(solved, total))}</text>',
            f'<text x="{x + 16}" y="234" fill="#ffffff" font-size="28" font-weight="700">{solved}'
            f'<tspan fill="#8b949e" font-size="14" font-weight="400"> / {total:,}</tspan></text>',
            f'<rect x="{x + 16}" y="250" width="{bar_w}" height="{bar_h}" rx="4" fill="#21262d"/>',
        ]
        if fill > 0:
            out.append(f'<rect x="{x + 16}" y="250" width="{fill:.2f}" height="{bar_h}" rx="4" fill="{color}"/>')

    out += ["</g>", "</svg>", ""]
    return "\n".join(out)


def render_stats(readme, counts, totals, username):
    """Return readme with the stats block replaced by the card image and profile link."""

    profile = f"https://leetcode.com/u/{username}/"
    lines = [
        '<p align="center">',
        f'  <a href="{profile}"><img src="{SVG_PATH}" width="600" alt={quoteattr(alt_text(counts, totals, username))}></a>',
        "</p>",
        "",
        f'<p align="center"><samp>Profile: <a href="{profile}">{escape(username)}</a></samp></p>',
    ]

    if not STATS_BLOCK.search(readme):
        raise ValueError("README.md is missing the LEETCODE-STATS markers.")

    return STATS_BLOCK.sub(lambda m: m[1] + "\n".join(lines) + "\n" + m[2], readme)


def update_files(data, requested, readme_path, svg_path):
    """Validate everything before writing, so a bad response or README leaves both files untouched."""

    username, counts, totals = parse_counts(data, requested)
    readme = render_stats(readme_path.read_text(encoding="utf-8"), counts, totals, username)
    svg = render_svg(counts, totals, username)
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_text(svg, encoding="utf-8", newline="\n")
    readme_path.write_text(readme, encoding="utf-8")
    return username, counts


def _self_test():

    def response(solved, totals=(4100, 975, 2138, 987), name="Someone"):
        def rows(values):
            return [{"difficulty": d, "count": c} for d, c in zip(("All",) + DIFFICULTIES, values)]
        return {"data": {"allQuestionsCount": rows(totals),
                         "matchedUser": {"username": name, "submitStats": {"acSubmissionNum": rows(solved)}}}}

    username, counts, totals = parse_counts(response((4, 2, 1, 1)), "someone")
    assert username == "Someone" and counts == {"All": 4, "Easy": 2, "Medium": 1, "Hard": 1}
    assert totals == {"All": 4100, "Easy": 975, "Medium": 2138, "Hard": 987}

    bad_responses = [
        {"errors": [{"message": "That user does not exist."}], "data": {"matchedUser": None}},
        {"data": None},
        {"data": {"matchedUser": {"username": "x", "submitStats": {"acSubmissionNum": [{"difficulty": "All", "count": 1}]}}}},
        {"data": {"matchedUser": response((1, 1, 0, 0))["data"]["matchedUser"]}},  # no question totals
        response((1, 1, 0, "0")),
        response((1, 1, 0, 0), totals=(4100, 975, 2138, -1)),
    ]
    for bad in bad_responses:
        try:
            parse_counts(bad, "x")
        except ValueError:
            continue
        raise AssertionError(f"accepted bad response {bad!r}")

    # Progress maths.
    assert fraction(0, 100) == 0 and fraction(50, 100) == 0.5 and fraction(5, 0) == 0 and fraction(200, 100) == 1
    assert percent_label(0, 975) == "0%" and percent_label(2, 975) == "0.2%" and percent_label(487, 975) == "50%"
    assert percent_label(975, 975) == "100%" and percent_label(3, 0) == "–" and percent_label(2, 4100) == "<0.1%"
    assert bar_width(0, 975, 140, 8) == 0 and bar_width(2, 975, 140, 8) == 8
    assert bar_width(975, 975, 140, 8) == 140 and abs(bar_width(487, 974, 140, 8) - 70) < 1e-9
    assert bar_width(4, 0, 140, 8) == 0

    def check_svg(svg):
        root = ET.fromstring(svg)  # raises on invalid XML
        assert root.tag == "{http://www.w3.org/2000/svg}svg" and root.get("viewBox") == "0 0 600 300"
        assert "<script" not in svg and "href" not in svg  # GitHub blocks scripts and external refs
        return root

    text = "".join(check_svg(render_svg(counts, totals, username)).itertext())
    for fragment in ("Easy", "Medium", "Hard", "2 / 975", "1 / 2,138", "1 / 987", "0.2%", "of 4,100 problems", "@Someone"):
        assert fragment in text, fragment

    # Zero solved: no filled bars or ring arc, 0% everywhere.
    zero = {"All": 0, "Easy": 0, "Medium": 0, "Hard": 0}
    svg = render_svg(zero, totals, "x")
    check_svg(svg)
    assert "stroke-dasharray" not in svg and svg.count(">0%<") == 4
    for name in DIFFICULTIES:
        assert f'rx="4" fill="{COLORS[name]}"' not in svg

    # A tiny share renders "<0.1%", which must be escaped.
    assert "<0.1%" in "".join(check_svg(render_svg({"All": 2, "Easy": 2, "Medium": 0, "Hard": 0}, totals, "x")).itertext())

    # Zero questions (no division by zero) and names that need escaping still give valid SVG.
    check_svg(render_svg(counts, zero, 'a<b&"c'))

    readme = "a\n<!-- LEETCODE-STATS:START -->\nold\n<!-- LEETCODE-STATS:END -->\nb"
    updated = render_stats(readme, counts, totals, username)
    assert 'href="https://leetcode.com/u/Someone/"' in updated and f'src="{SVG_PATH}"' in updated
    assert updated.startswith("a\n<!-- LEETCODE-STATS:START -->") and updated.endswith("<!-- LEETCODE-STATS:END -->\nb")
    assert "4 solved (Easy 2 of 975, Medium 1 of 2138, Hard 1 of 987)" in updated
    assert "old" not in updated
    assert render_stats(updated, counts, totals, username) == updated  # stable, so unchanged stats make no commit

    try:
        render_stats("no markers", counts, totals, username)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted README without markers")

    # On disk: good data writes both files; bad data or a broken README writes neither.
    with tempfile.TemporaryDirectory() as tmp:
        readme_path, svg_path = Path(tmp, "README.md"), Path(tmp, SVG_PATH)
        readme_path.write_text(readme, encoding="utf-8")
        update_files(response((4, 2, 1, 1)), "someone", readme_path, svg_path)
        good_readme, good_svg = readme_path.read_text(encoding="utf-8"), svg_path.read_text(encoding="utf-8")
        check_svg(good_svg)

        for bad in bad_responses:
            try:
                update_files(bad, "x", readme_path, svg_path)
            except ValueError:
                pass
            assert readme_path.read_text(encoding="utf-8") == good_readme
            assert svg_path.read_text(encoding="utf-8") == good_svg

        readme_path.write_text("no markers", encoding="utf-8")
        try:
            update_files(response((9, 9, 0, 0)), "someone", readme_path, svg_path)
        except ValueError:
            pass
        assert svg_path.read_text(encoding="utf-8") == good_svg

    print("Self-test passed.")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _self_test()
        sys.exit(0)

    requested = os.environ.get("LEETCODE_USERNAME", "").strip()

    if not requested:
        sys.exit("Set LEETCODE_USERNAME to your LeetCode username.")

    username, counts = update_files(fetch_profile(requested), requested, Path("README.md"), Path(SVG_PATH))
    print(f"Updated README.md and {SVG_PATH} for {username}: {counts}")
