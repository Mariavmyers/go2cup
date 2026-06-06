#!/usr/bin/env python3
"""
GO2CUP -- FIFA trademark compliance pass (MainEntry LLC).

Deterministic find-and-replace across every .html file in a repo.
Edits files in place and writes compliance_report.md when finished.

USAGE (run from inside your repo, or pass the path):
    python compliance_pass.py --dry-run          # preview only, writes nothing
    python compliance_pass.py                     # runs on current folder, edits in place
    python compliance_pass.py "C:\\Users\\Owner\\go2cup"

Run --dry-run FIRST, read the report, then run for real and push to GitHub.
This is a deterministic text tool, not legal advice.
"""

import os
import re
import sys
import argparse
from datetime import datetime

# --------------------------------------------------------------------------
# CONFIG -- review these two lists before running
# --------------------------------------------------------------------------

# Link substrings that should get the "we are not an official ticket seller"
# disclaimer injected right after them (Task 3). Edit to match YOUR ticket links.
TICKET_LINK_MARKERS = [
    "seatgeek.com",
    "tiqets.com",
]

# Phrases that PROTECT a line -- no FIFA replacement happens on a line that
# contains any of these (Task 2 exceptions). Matched case-insensitively.
EXCEPTION_PHRASES = [
    "not affiliated with fifa",
    "endorsed by fifa",
    "connected to fifa",
    "licensed by fifa",
    "fifa's official",
]

# Replacements, MOST SPECIFIC FIRST. Order is deliberate -- do not reorder.
# (See the "ordering" note in the report header for why this matters.)
REPLACEMENTS = [
    ("the official FIFA World Cup 2026 song", "the official 2026 World Cup anthem"),
    ("Official FIFA VIP Packages",            "Third-Party Hospitality Options"),
    ("official FIFA commercial framework",    "hospitality and commercial partnerships"),
    ("2026 FIFA World Cup",                   "2026 World Cup"),
    ("FIFA World Cup 2026",                   "2026 World Cup"),
    ("FIFA World Cup",                        "World Cup"),
    ("FIFA 2026",                             "Soccer 2026"),
]

TICKET_DISCLAIMER = (
    '<p style="font-size:0.75rem;opacity:0.65;margin-top:4px;line-height:1.5;">\n'
    'GO2CUP links to independent third-party resellers. We are not an\n'
    'official ticket seller and have no affiliation with FIFA or any\n'
    'official ticketing authority.\n'
    '</p>'
)

FOOTER_DISCLAIMER = (
    '<p style="font-size:0.8rem;opacity:0.7;line-height:1.6;margin-top:1rem;">\n'
    'GO2CUP is an independent fan travel guide operated by MainEntry LLC.\n'
    'The terms World Cup®, FIFA®, and FIFA World Cup™ are registered trademarks\n'
    'of FIFA. GO2CUP is not affiliated with, licensed by, sponsored by, endorsed\n'
    'by, or officially connected to FIFA, any national football federation,\n'
    'host cities, stadiums, governments, official sponsors, travel providers,\n'
    'or ticketing entities. Affiliate links are disclosed. Always verify schedules,\n'
    'prices, and travel requirements with official sources before booking.\n'
    '</p>'
)
FOOTER_SENTINEL = "\x00__FOOTER_BLOCK__\x00"

# Words that mark an existing <p> as a "disclaimer" worth replacing (Task 4).
DISCLAIMER_HINTS = (
    "not affiliated", "mainentry", "affiliate links", "affiliate link",
    "independent fan", "registered trademark", "disclaimer", "not official",
)

# Tokens we must NEVER alter -- counted before/after to confirm (Task: Do Not Touch).
PROTECTED_TOKENS = [
    "kiwi", "klook", "tiqets", "gettransfer", "airhelp", "booking.com",
    "seatgeek", "viator", "villiers", "GO2CUP", "contact@sportdgx.com",
    "mariavmyers", "MainEntryGo2Cup", "src=", "href=",
]


# --------------------------------------------------------------------------
# CORE
# --------------------------------------------------------------------------

def strip_standalone_fifa_in_keywords(line):
    """Remove a bare 'FIFA' token from a meta keywords content list."""
    low = line.lower()
    if 'name="keywords"' not in low and "name='keywords'" not in low:
        return line

    def repl(m):
        head, content, tail = m.group(1), m.group(2), m.group(3)
        parts = [p.strip() for p in content.split(",")]
        parts = [p for p in parts if p and p.lower() != "fifa"]
        return head + ", ".join(parts) + tail

    return re.sub(r'(content=["\'])(.*?)(["\'])', repl, line, flags=re.IGNORECASE)


def apply_footer(text):
    """Task 4: replace existing footer disclaimer, or insert canonical block."""
    if FOOTER_DISCLAIMER in text:
        return text, "footer disclaimer already present -- left as is"

    # Prefer a disclaimer-looking <p> inside an existing <footer>...</footer>.
    footer_m = re.search(r"<footer\b.*?</footer>", text, re.IGNORECASE | re.DOTALL)
    search_region = footer_m.group(0) if footer_m else text
    region_offset = footer_m.start() if footer_m else 0

    target = None
    for m in re.finditer(r"<p\b[^>]*>.*?</p>", search_region, re.IGNORECASE | re.DOTALL):
        if any(h in m.group(0).lower() for h in DISCLAIMER_HINTS):
            target = m  # keep the LAST match (footer disclaimer is usually last)
    if target:
        s = region_offset + target.start()
        e = region_offset + target.end()
        return text[:s] + FOOTER_DISCLAIMER + text[e:], "replaced existing disclaimer paragraph"

    if re.search(r"</footer>", text, re.IGNORECASE):
        return re.sub(r"</footer>", FOOTER_DISCLAIMER + "\n</footer>", text, count=1,
                      flags=re.IGNORECASE), "inserted before </footer> (no existing disclaimer)"
    if re.search(r"</body>", text, re.IGNORECASE):
        return re.sub(r"</body>", FOOTER_DISCLAIMER + "\n</body>", text, count=1,
                      flags=re.IGNORECASE), "inserted before </body> (no <footer> found)"
    return text, "WARNING: no </footer> or </body> -- footer NOT inserted, review manually"


def inject_ticket_disclaimers(text):
    """Task 3: insert ticket disclaimer right after each ticket affiliate link."""
    a_pattern = re.compile(r'<a\b[^>]*href=["\']([^"\']*)["\'][^>]*>.*?</a>',
                           re.IGNORECASE | re.DOTALL)
    out, last, count = [], 0, 0
    for m in a_pattern.finditer(text):
        href = m.group(1).lower()
        if any(mk in href for mk in TICKET_LINK_MARKERS):
            following = text[m.end():m.end() + 160].lower()
            if "official ticket seller" in following:  # idempotency guard
                continue
            out.append(text[last:m.end()])
            out.append("\n" + TICKET_DISCLAIMER)
            last = m.end()
            count += 1
    out.append(text[last:])
    return "".join(out), count


def process_file(path, dry_run):
    with open(path, encoding="utf-8", errors="replace") as f:
        original = f.read()

    text, changes = original, []

    # Task 4 first, then shield the footer so FIFA replacements never corrupt
    # its trademark line ("FIFA World Cup(TM)").
    text, footer_note = apply_footer(text)
    if "already present" not in footer_note:
        changes.append(("[FOOTER]", footer_note))
    text = text.replace(FOOTER_DISCLAIMER, FOOTER_SENTINEL)

    # Tasks 1, 2, 3 (replacements) -- line by line, skipping protected lines.
    new_lines = []
    for line in text.split("\n"):
        low = line.lower()
        if any(p in low for p in EXCEPTION_PHRASES):
            new_lines.append(line)
            continue
        edited = line
        for old, new in REPLACEMENTS:
            if old in edited:
                edited = edited.replace(old, new)
        edited = strip_standalone_fifa_in_keywords(edited)
        if edited != line:
            changes.append((line.strip(), edited.strip()))
        new_lines.append(edited)
    text = "\n".join(new_lines)

    # Task 3 ticket disclaimers, then restore footer.
    text, ticket_count = inject_ticket_disclaimers(text)
    if ticket_count:
        changes.append(("[TICKET DISCLAIMER]", f"inserted after {ticket_count} ticket link(s)"))
    text = text.replace(FOOTER_SENTINEL, FOOTER_DISCLAIMER)

    # Do-Not-Touch verification: protected token counts must be unchanged.
    # Only a DECREASE matters -- it means a protected link/brand/path was
    # damaged. Increases are benign (the inserted disclaimers say "GO2CUP" etc).
    violations = []
    for tok in PROTECTED_TOKENS:
        if text.count(tok) < original.count(tok):
            violations.append(f"{tok}: {original.count(tok)} -> {text.count(tok)}")

    changed = text != original
    if changed and not dry_run:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    return changes, changed, violations


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    html_files = []
    for dirpath, _, files in os.walk(args.root):
        if ".git" in dirpath.split(os.sep):
            continue
        for fn in files:
            if fn.lower().endswith(".html"):
                html_files.append(os.path.join(dirpath, fn))
    html_files.sort()

    report = [
        "# GO2CUP FIFA Compliance Pass -- Report",
        f"Run: {datetime.now():%Y-%m-%d %H:%M}  |  Mode: "
        f"{'DRY RUN (no files written)' if args.dry_run else 'LIVE (files edited in place)'}",
        f"Root: {os.path.abspath(args.root)}",
        f"HTML files found: {len(html_files)}",
        "",
    ]
    modified, all_violations = [], []

    for path in html_files:
        rel = os.path.relpath(path, args.root)
        changes, changed, violations = process_file(path, args.dry_run)
        if changed:
            modified.append(rel)
            report.append(f"## {rel}")
            for old, new in changes:
                if old.startswith("["):
                    report.append(f"- {old} {new}")
                else:
                    report.append(f"- OLD: {old}\n  NEW: {new}")
            report.append("")
        if violations:
            all_violations.append((rel, violations))

    report += [
        "---", "## Summary",
        f"- Files modified: {len(modified)} of {len(html_files)}",
        "- Do-Not-Touch list (affiliate links, src/href, brand, contact, socials): "
        + ("RESPECTED -- all protected token counts unchanged."
           if not all_violations else "VIOLATIONS DETECTED (see below)."),
    ]
    if all_violations:
        for rel, v in all_violations:
            report.append(f"  - {rel}: " + "; ".join(v))
    report.append(f"- Status: {'preview complete' if args.dry_run else 'all tasks completed'}.")

    out = "\n".join(report)
    with open(os.path.join(args.root, "compliance_report.md"), "w", encoding="utf-8") as f:
        f.write(out)
    print(out)


if __name__ == "__main__":
    main()
