"""Update the README progress card from a public LeetCode profile.

Needs no cookies: matchedUser and allQuestionsCount are readable by anyone,
like the profile page. Writes an SVG card next to the README, because GitHub
strips inline SVG from Markdown.
"""

import base64
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
COLORS = {"Easy": "#00b8a3", "Medium": "#ffc01e", "Hard": "#ff375f"}

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


# Same typeface, grey ink and motion as the profile README graphics (yo5on/yo5on), so the card sits
# in that page's visual language; JBMono is inlined because <img> SVGs cannot fetch fonts.
FONT_DIR = Path(__file__).resolve().parent / "fonts"
MONO = "JBMono,ui-monospace,SFMono-Regular,Menlo,Consolas,&apos;Liberation Mono&apos;,monospace"
INK = (
    ".e-f{fill:#424a53}.m-f{fill:#8c959f}.d-f{fill:#6e7681}.w{fill:#6e7681;opacity:.13}"
    "@media(prefers-color-scheme:dark){.e-f{fill:#f0f6fc}.m-f{fill:#8b949e}.d-f{fill:#c9d1d9}"
    ".w{fill:#c9d1d9;opacity:.16}}"
)

# Official LeetCode mark in its original colours (devicon leetcode-original, MIT), 128x128.
LOGO_DASH = (
    "M117.555 76.558c0-3.957-3.008-7.178-6.72-7.178H57.159c-3.712 0-6.72 3.221-6.72 7.178 0 3.958 3.002 7.18 6.72 "
    "7.18h53.676c3.712.005 6.72-3.217 6.72-7.18"
)
LOGO_BODY = (
    "m18.79 96.996 23.003 23.26c5.19 5.221 12.363 7.744 20.283 7.744s15.094-2.73 20.294-7.968l13.803-14.065c2.72-"
    "2.741 2.624-7.28-.208-10.133-2.832-2.854-7.333-2.95-10.048-.208L71.645 109.53c-2.465 2.49-5.878 3.53-9.649 "
    "3.53s-7.179-1.04-9.653-3.53L29.419 86.26c-2.47-2.49-3.712-6.133-3.712-9.936s1.243-7.238 3.712-9.728l22.854-"
    "23.361c2.47-2.49 5.952-3.44 9.718-3.44s7.179 1.04 9.648 3.53l14.273 13.9c2.72 2.746 7.221 2.65 10.053-.203 "
    "2.832-2.859 2.928-7.398.208-10.14L82.37 32.825a26.64 26.64 0 0 0-12.758-7.094l-.18-.037 13.05-13.35c2.73-"
    "2.741 2.635-7.285-.197-10.139S74.945-.74 72.22 2.002L18.79 55.87c-5.19 5.237-7.905 12.464-7.905 20.454S13.6 "
    "91.77 18.79 96.996"
)
LOGO_SHADE = (
    "M43.5 121.674a11.3 11.3 0 0 1-2.528-1.925c-7.078-7.11-14.187-14.187-21.249-21.318C9.115 87.721 7.445 72.1 "
    "15.531 59.39a32 32 0 0 1 4.475-5.355L71.33 2.605c3.333-3.34 7.99-3.478 11.088-.358 2.987 3.003 2.81 7.76-.416 "
    "11.019-4.101 4.139-8.208 8.267-12.315 12.4-.219.651-.747 1.067-1.2 1.531-4.603 4.672-9.334 9.222-13.872 "
    "13.963-.592.619-1.398.992-1.984 1.627-7.59 7.59-15.27 15.094-22.753 22.784-6.054 6.225-5.85 15.67.363 22.012 "
    "6.976 7.125 14.075 14.134 21.126 21.195.357.357.725.704 1.088 1.056 2.496 1.616 2.528 6.667.976 8.912-1.712 "
    "2.48-3.947 4-7.11 3.883-1.061-.032-1.936-.458-2.821-.955"
)
# LeetCode's signature orange, and the lighter yellow its site uses for highlights.
BRAND, BRAND_LIGHT = "#ffa116", "#ffc01e"
# The black part of the mark turns white on dark backgrounds, as on LeetCode's own dark theme.
LOGO_INK = ".k{fill:#070706}@media(prefers-color-scheme:dark){.k{fill:#ffffff}}"


def _font_face(filename, weight):

    data = base64.b64encode((FONT_DIR / filename).read_bytes()).decode("ascii")
    return (f"@font-face{{font-family:JBMono;font-style:normal;font-weight:{weight};font-display:block;"
            f"src:url(data:font/woff2;base64,{data}) format('woff2')}}")


def _fade(begin, body):
    """The profile's entrance: fade in once and stay."""

    return (f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" '
            f'dur="0.45s" fill="freeze"/>{body}</g>')


def render_svg(counts, totals, username):
    """Return a self-contained 620x180 animated SVG card (SMIL only: no scripts or external refs)."""

    w, h = 620, 180
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" '
        f'font-family="{MONO}" role="img" aria-labelledby="title">'
        f'<title id="title">{escape(alt_text(counts, totals, username))}</title>',
        f'<style>{_font_face("jbmono-400.woff2", 400)}{_font_face("jbmono-600.woff2", 600)}{INK}{LOGO_INK}</style>',
        # A light band sweeps across the orange body every 5s; pad keeps the base colour outside it.
        '<defs><linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="-64" y1="0" x2="64" y2="0">'
        f'<stop offset="0" stop-color="#e7a41f"/><stop offset=".4" stop-color="{BRAND}"/>'
        f'<stop offset=".5" stop-color="{BRAND_LIGHT}"/><stop offset=".6" stop-color="{BRAND}"/>'
        '<stop offset="1" stop-color="#e7a41f"/>'
        '<animateTransform attributeName="gradientTransform" type="translate" values="-64 0;192 0;192 0" '
        'keyTimes="0;.45;1" begin="1.2s" dur="5s" repeatCount="indefinite"/></linearGradient>'
        '<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5"/></filter>'
        '<filter id="tglow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>'
        # The profile's wipe-and-cursor entrance, here revealing the logo.
        '<clipPath id="reveal"><rect x="0" y="0" height="112" width="0">'
        '<animate attributeName="width" from="0" to="108" begin="0.10s" dur="0.8s" fill="freeze"/></rect></clipPath>'
        '</defs>',
    ]

    # Glow behind the mark breathes in LeetCode orange once it is revealed.
    pulse = '<animate attributeName="opacity" values=".15;.55;.15" begin="0.9s" dur="3s" repeatCount="indefinite"/>'
    out += [
        '<g clip-path="url(#reveal)"><g transform="translate(4 8) scale(.75)">',
        f'<path d="{LOGO_BODY}" fill="{BRAND}" filter="url(#glow)" opacity="0">{pulse}</path>',
        f'<path d="{LOGO_DASH}" fill="#b3b1b0"/>',
        f'<path d="{LOGO_BODY}" fill="url(#shine)"/>',
        f'<path d="{LOGO_SHADE}" class="k"/>',
        "</g></g>",
        f'<rect y="4" width="2" height="104" fill="{BRAND}" opacity="0">'
        '<animate attributeName="x" from="0" to="108" begin="0.10s" dur="0.8s" fill="freeze"/>'
        '<set attributeName="opacity" to="0.7" begin="0.10s"/><set attributeName="opacity" to="0" begin="0.90s"/>'
        "</rect>",
    ]

    pct = percent_label(counts["All"], totals["All"])
    out += [
        _fade(0.10, f'<text x="124" y="58" fill="{BRAND}" font-size="52" font-weight="600" filter="url(#tglow)" '
                    f'opacity="0">{counts["All"]}{pulse}</text>'
                    f'<text x="124" y="58" fill="{BRAND}" font-size="52" font-weight="600">{counts["All"]}</text>'
                    f'<text x="124" y="80" class="m-f" font-size="12">problems solved · of {totals["All"]:,}</text>'),
        _fade(0.30, f'<text x="{w}" y="30" fill="{BRAND}" font-size="19" text-anchor="end" font-weight="600">'
                    f'{escape(pct)}</text>'
                    f'<text x="{w}" y="47" class="m-f" font-size="11" text-anchor="end">of all problems</text>'),
        _fade(0.42, f'<text x="{w}" y="70" class="e-f" font-size="19" text-anchor="end" font-weight="600">'
                    f'@{escape(username)}</text>'
                    f'<text x="{w}" y="87" class="m-f" font-size="11" text-anchor="end">leetcode</text>'),
    ]

    # Difficulty rows, revealed by the profile's wipe + scanning cursor.
    bar_x, bar_w, bar_h, top = 96, 416, 7, 118
    out.append(f'<clipPath id="wipe"><rect x="{bar_x}" y="{top}" height="60" width="0">'
               f'<animate attributeName="width" from="0" to="{bar_w}" begin="0.60s" dur="0.95s" fill="freeze"/>'
               '</rect></clipPath>')
    for i, name in enumerate(DIFFICULTIES):
        y = top + 16 + i * 22
        solved, total = counts[name], totals[name]
        fill = bar_width(solved, total, bar_w, bar_h)
        out.append(_fade(0.50 + i * 0.05,
                         f'<text x="0" y="{y}" fill="{COLORS[name]}" font-size="11" font-weight="600">'
                         f'{name.lower()}</text>'
                         f'<rect x="{bar_x}" y="{y - 8}" width="{bar_w}" height="{bar_h}" rx="3.5" class="w"/>'
                         f'<text x="{w}" y="{y}" class="e-f" font-size="11" text-anchor="end">{solved}'
                         f'<tspan class="m-f"> / {total:,}</tspan></text>'))
        if fill > 0:
            out.append(f'<g clip-path="url(#wipe)"><rect x="{bar_x}" y="{y - 8}" width="{fill:.2f}" '
                       f'height="{bar_h}" rx="3.5" fill="{COLORS[name]}"/></g>')
    out += [
        f'<rect y="{top}" width="2" height="60" fill="{BRAND}" opacity="0">'
        f'<animate attributeName="x" from="{bar_x}" to="{bar_x + bar_w}" begin="0.60s" dur="0.95s" fill="freeze"/>'
        '<set attributeName="opacity" to="0.55" begin="0.60s"/><set attributeName="opacity" to="0" begin="1.55s"/>'
        "</rect>",
        "</svg>",
        "",
    ]
    return "\n".join(out)


def render_stats(readme, counts, totals, username):
    """Return readme with the stats block replaced by the card image and profile link."""

    profile = f"https://leetcode.com/u/{username}/"
    lines = [
        '<p align="center">',
        f'  <a href="{profile}"><img src="{SVG_PATH}" width="620" alt={quoteattr(alt_text(counts, totals, username))}></a>',
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
        assert root.tag == "{http://www.w3.org/2000/svg}svg" and root.get("viewBox") == "0 0 620 180"
        assert "<script" not in svg and "href" not in svg  # GitHub blocks scripts and external refs
        return root

    text = "".join(check_svg(render_svg(counts, totals, username)).itertext())
    for fragment in ("easy", "medium", "hard", "2 / 975", "1 / 2,138", "1 / 987", "0.1%", "of 4,100", "@Someone"):
        assert fragment in text, fragment

    # Zero solved: no filled bars, 0% overall.
    zero = {"All": 0, "Easy": 0, "Medium": 0, "Hard": 0}
    svg = render_svg(zero, totals, "x")
    check_svg(svg)
    assert svg.count(">0%<") == 1 and 'clip-path="url(#wipe)"' not in svg

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
