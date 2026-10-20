"""`standards init` — vendor the kit into a target repo and write the marker."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from standards.__about__ import __version__
from standards.managed import (
    Block,
    block_hash,
    extract_block,
    find_block,
    has_begin_marker,
    splice_block,
)
from standards.manifest import (
    AGENTS,
    PROFILE_TEMPLATED,
    SCAFFOLD_ONCE,
    classify,
    iter_payload,
    unused_hook_file,
)
from standards.marker import MARKER_NAME, read_marker, sha256_file, write_marker
from standards.payload import payload_root
from standards.profiles import EXTRAS, MATRIX, needed_docs, parse_profiles

ADOPT_REPORT_KEYS = ("added", "unchanged", "spliced", "conflicts", "scaffolded")

CHECKLIST = "docs/STANDARDS-CHECKLIST.md"
PROFILE_LINE_RE = re.compile(r"\*\*Profile:\*\*[^\n]*")
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_FENCE = r"^[ \t]*(`{3,}|~{3,})[^\n]*\n.*?^[ \t]*\1[ \t]*$"
# Examples that are never edited: comments, fenced blocks, and inline code. A code
# span opens and closes with backtick runs of the same length, so ``**Profile:** x``
# is one span, not two empty ones.
HIDDEN_RE = re.compile(rf"<!--.*?-->|{_FENCE}|(?<!`)(`+)(?!`)[^\n]*?(?<!`)\2(?!`)",
                       re.DOTALL | re.MULTILINE)
# Where a doc mention doesn't count. Inline code does count: rows name docs in it.
UNCOUNTED_RE = re.compile(rf"<!--.*?-->|{_FENCE}", re.DOTALL | re.MULTILINE)
# Template rows that setup replaces; a hand-written checklist may have neither.
PLACEHOLDER_ROWS = {
    "## Profile-required": "- [ ] <doc> — <one-line note if helpful>\n",
    "## Profile-expected": "- [ ] <doc>\n",
}
ROOT_STARTER_DESTS = frozenset({"README.md", "CHANGELOG.md"})
# ADR-0023: new adoptions enforce the drift Stop hook. Markers written before it
# have no `hook_mode`, so existing adopters keep advising until they opt in.
NEW_ADOPTION_KEYS: dict[str, object] = {"hook_mode": "enforce"}

_LEADING_COMMENT_RE = re.compile(r"\A\s*<!--.*?-->\s*", re.DOTALL)


def _require_block(text: str, file: str) -> Block:
    """Return the lone kit-managed block, or fail loud naming the file.

    Partial payload files always carry exactly one well-formed block; a None here
    means a corrupt managed region, which must surface clearly rather than crash
    with AttributeError deep in the copy loop.
    """
    block = find_block(text)
    if block is None:
        raise ValueError(f"{file}: expected exactly one kit-managed block, found none")
    return block


def _require_hash(text: str, file: str) -> str:
    """Hash of the file's managed-block inner content, or fail loud naming the file."""
    digest = block_hash(text)
    if digest is None:
        raise ValueError(f"{file}: expected exactly one kit-managed block, found none")
    return digest


def _stamp_ai_starter(content: str, adopted: str) -> str:
    """Make a scaffolded ai/ file pass the freshness check on day one.

    The starters lead with an HTML comment, which hides the frontmatter from the
    `^---` parser, and carry placeholder dates. Strip the comment and stamp the
    adopted date so `last_updated:` / `written:` are real, parseable, and fresh.
    """
    content = _LEADING_COMMENT_RE.sub("", content, count=1)
    content = content.replace("last_updated: YYYY-MM-DD", f"last_updated: {adopted}")
    content = content.replace(
        "written: YYYY-MM-DDTHH:MM:SS-05:00", f"written: {adopted}"
    )
    return content


def _first_visible(pattern: str, text: str, after: int = 0) -> re.Match | None:
    """The first match at or past `after` that isn't inside a comment or inline code,
    so examples such as `<!-- **Profile:** library -->` are never edited."""
    hidden = [m.span() for m in HIDDEN_RE.finditer(text)]
    return next((m for m in re.finditer(pattern, text, re.MULTILINE)
                 if m.start() >= after and not any(a <= m.start() < b for a, b in hidden)),
                None)


def _add_rows(text: str, heading: str, rows: str) -> str:
    """Add rows to a checklist section: in place of the template's placeholder row, at
    the end of the section, or in a new section before `## Notes` (else at the end)."""
    if not rows:
        return text
    placeholder = PLACEHOLDER_ROWS.get(heading)
    spot = _first_visible(re.escape(placeholder), text) if placeholder else None
    if spot:
        return text[:spot.start()] + rows + text[spot.end():]
    found = _first_visible(rf"^{re.escape(heading)}[ \t]*$", text)
    if found is None:
        notes = _first_visible(r"^## Notes[ \t]*$", text)
        at = notes.start() if notes else len(text)
        head = text[:at].rstrip("\n")
        return f"{head}\n\n{heading}\n\n{rows}" + ("\n" + text[at:] if notes else "")
    nxt = _first_visible(r"^## ", text, after=found.end())
    end = nxt.start() if nxt else len(text)
    body = text[found.end():end].rstrip("\n")
    gap = "\n" if body.rsplit("\n", 1)[-1].lstrip().startswith("- ") else "\n\n"
    return text[:found.end()] + body + gap + rows + ("\n" if end < len(text) else "") + text[end:]


def reconcile_checklist(text: str, profiles: list[str]) -> str:
    """Point a checklist at these profiles without touching the adopter's own lines.

    Rewrite the `**Profile:**` line, then add ticked rows for the Required and
    Expected docs it doesn't mention yet (setup creates them) and plain bullets for
    missing extras (setup doesn't create those, and an unticked box needs a
    waiver). Mentions inside HTML comments don't count. Running it twice is a no-op.
    """
    header = "**Profile:** " + " + ".join(profiles)
    line = _first_visible(PROFILE_LINE_RE.pattern, text)
    if line:
        old, end = line.group(0), line.end()
        opener = old.rfind("<!--")
        if opener != -1 and "-->" not in old[opener:]:  # a comment that runs on stays whole
            old, end = old[:opener], line.start() + opener
        # Replace every old name, but keep the line's comments.
        notes = "".join(f" {c}" for c in COMMENT_RE.findall(old))
        text = text[:line.start()] + header + notes + (" " if end < line.end() else "") + text[end:]
    else:
        title = re.search(r"^# .*$", text, re.MULTILINE)
        at = title.end() + 1 if title else 0
        text = f"{text[:at]}\n{header}\n{text[at:]}"
    required, expected = needed_docs(profiles)
    sections = (
        ("## Profile-required", [(f"docs/{d}", f"- [x] `docs/{d}`\n") for d in required]),
        ("## Profile-expected", [(f"docs/{d}", f"- [x] `docs/{d}`\n") for d in expected]),
        ("## Profile extras", [(EXTRAS[p], f"- `{EXTRAS[p]}` ({p} extra)\n") for p in profiles]),
    )
    for heading, items in sections:
        visible = UNCOUNTED_RE.sub("", text)
        text = _add_rows(text, heading, "".join(row for key, row in items if key not in visible))
    return text


def _point_checklist(target: Path, profiles: list[str]) -> bool:
    """Reconcile an existing checklist with the profiles; True if it changed."""
    path = target / CHECKLIST
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    new = reconcile_checklist(text, profiles)
    if new != text:
        path.write_text(new, encoding="utf-8")
    return new != text


def _fill_checklist(content: str, *, profiles: list[str], adopted: str, repo_name: str) -> str:
    """Seed the checklist so a freshly adopted repo is CI-green: fill the header
    metadata, tick the universal-core boxes, and point it at the profiles."""
    content = content.replace("# Standards Checklist — <repo-name>",
                              f"# Standards Checklist — {repo_name}")
    content = content.replace("**Kit version adopted:** <e.g. 0.1.0>",
                              f"**Kit version adopted:** {__version__}")
    content = content.replace("**Last reviewed:** YYYY-MM-DD by <name>",
                              f"**Last reviewed:** {adopted} by standards init")
    out, in_core = [], False
    for line in content.splitlines(keepends=True):
        if line.lstrip().startswith("## "):
            in_core = line.lstrip()[3:].strip().lower().startswith("universal core")
        if in_core:
            line = line.replace("- [ ] ", "- [x] ", 1)
        out.append(line)
    return reconcile_checklist("".join(out), profiles)


def _fill_root_starter(content: str, *, profile: str, adopted: str,
                       repo_name: str) -> str:
    """Fill starter README/CHANGELOG metadata without claiming repo specifics."""
    return (
        content.replace("<repo-name>", repo_name)
        .replace("<profile>", profile)
        .replace("<kit-version>", __version__)
        .replace("<adopted-date>", adopted)
    )


def _seed_scaffold_once(target: Path, src_root: Path, *, profiles: list[str],
                        adopted: str) -> list[str]:
    """Seed scaffold-once files into `target` (only those absent). Returns the
    destination paths actually written. Each seed is transformed so a freshly
    adopted repo is CI-green: tick the checklist boxes, stamp the ai/ dates. The
    profiles' Required and Expected docs are created from their templates.
    """
    repo_name = target.resolve().name
    seeded: list[str] = []
    for src_rel, dest_rel in SCAFFOLD_ONCE.items():
        dest = target / dest_rel
        if dest.exists():
            continue
        content = (src_root / src_rel).read_text(encoding="utf-8")
        if dest_rel in PROFILE_TEMPLATED:
            content = _fill_checklist(content, profiles=profiles, adopted=adopted,
                                      repo_name=repo_name)
        elif dest_rel in ROOT_STARTER_DESTS:
            content = _fill_root_starter(content, profile=" + ".join(profiles),
                                         adopted=adopted, repo_name=repo_name)
        elif dest_rel.startswith("ai/"):
            content = _stamp_ai_starter(content, adopted)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        seeded.append(dest_rel)
    return seeded + _create_profile_docs(target, src_root, profiles)


def _create_profile_docs(target: Path, src_root: Path, profiles: list[str]) -> list[str]:
    """Create the profiles' Required and Expected docs from their templates, never
    overwriting one. Returns the paths created."""
    required, expected = needed_docs(profiles)
    created: list[str] = []
    for doc in sorted(required + expected):
        dest = target / "docs" / doc
        if dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src_root / "docs" / "templates" / MATRIX[doc][0], dest)
        created.append(f"docs/{doc}")
    return created


def run_change(target: Path, *, profile: str | list[str]) -> dict[str, list[str]]:
    """Change what an adopted repo contains (ADR-0025): record the profiles, create the
    docs they newly need, and point the checklist at them. Never overwrites a doc,
    and leaves the kit version alone; that's `update`'s job.

    Returns {"created": [...], "checklist": [...]}. Raises ValueError for bad
    profiles, FileNotFoundError if the repo isn't adopted.
    """
    profiles = parse_profiles(profile)
    target = Path(target)
    marker = read_marker(target)
    if marker is None:
        raise FileNotFoundError(f"{target / MARKER_NAME} not found; set the repo up first")
    created = _create_profile_docs(target, payload_root(), profiles)
    checklist = [CHECKLIST] if _point_checklist(target, profiles) else []
    write_marker(target, kit_version=marker["kit_version"], profile=profiles,
                 adopted=marker.get("adopted", ""), tracked=marker.get("tracked", {}),
                 managed=marker.get("managed", {}), keep=marker)
    return {"created": created, "checklist": checklist}


def run_init(target: Path, *, profile: str | list[str], adopted: str, force: bool = False,
             agents=AGENTS) -> dict:
    """Copy kit-tracked files + scaffold-once seeds into `target`; write the marker.

    `agents` picks the one hook file the repo gets and is recorded in the marker.
    `profile` is one profile, a comma list, or a list (ADR-0025). Returns the marker
    dict. Raises ValueError for bad profiles, FileExistsError if already adopted
    and not force.
    """
    profiles = parse_profiles(profile)
    target = Path(target)
    previous = read_marker(target)
    if previous is not None and not force:
        raise FileExistsError(
            f"{target / MARKER_NAME} exists; pass force=True to re-init"
        )
    old_hooks = unused_hook_file(agents)
    if previous is not None and old_hooks in previous.get("tracked", {}) \
            and (target / old_hooks).exists():
        raise FileExistsError(
            f"{old_hooks} holds the kit's hooks for this repo's previous agents; delete it "
            f"before switching to {', '.join(agents)}, or Copilot runs each hook twice"
        )

    if not force:
        collisions: list[str] = []
        for full, rel in iter_payload(payload_root(), agents):
            cls = classify(rel)
            if cls == "scaffold-once-source":
                continue
            dest = target / rel
            if not dest.exists():
                continue
            if cls == "partial":
                differs = block_hash(dest.read_text(encoding="utf-8")) != \
                    block_hash(full.read_text(encoding="utf-8"))
            else:
                differs = sha256_file(dest) != sha256_file(full)
            if differs:
                collisions.append(rel)
        if collisions:
            shown = ", ".join(sorted(collisions)[:5])
            more = "" if len(collisions) <= 5 else f" (+{len(collisions) - 5} more)"
            raise FileExistsError(
                f"{len(collisions)} kit file(s) already exist with different content: "
                f"{shown}{more}. Run `standards adopt` to adopt non-destructively "
                f"(keeps your files, writes .kit-{__version__} sidecars), or re-run "
                f"with force=True to overwrite."
            )

    src_root = payload_root()
    tracked: dict[str, str] = {}
    managed: dict[str, str] = {}

    for full, rel in iter_payload(src_root, agents):
        cls = classify(rel)
        if cls == "scaffold-once-source":
            continue  # handled in the scaffold-once loop below
        dest = target / rel
        if cls == "partial" and dest.exists() and not force:
            # Preserve downstream content outside the managed block. The pre-flight
            # guard already ensured the existing block matches the payload's, so we
            # record the existing block's hash rather than overwriting the whole file.
            existing_hash = block_hash(dest.read_text(encoding="utf-8"))
            if existing_hash is not None:
                managed[rel] = existing_hash
                continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(full, dest)
        if cls == "partial":
            managed[rel] = _require_hash(dest.read_text(encoding="utf-8"), rel)
        else:  # kit-tracked
            tracked[rel] = sha256_file(dest)

    _seed_scaffold_once(target, src_root, profiles=profiles, adopted=adopted)
    _point_checklist(target, profiles)  # a checklist kept from before may name other profiles

    return write_marker(target, kit_version=__version__, profile=profiles,
                        adopted=adopted, tracked=tracked, managed=managed,
                        keep={**NEW_ADOPTION_KEYS, "agents": list(agents)})


def run_adopt(target: Path, *, profile: str | list[str], adopted: str,
              agents=AGENTS) -> dict[str, list[str]]:
    """Adopt the kit into an EXISTING repo non-destructively (RFC-0002 / ADR-0013).

    Like `init` but never clobbers: a differing kit-tracked file is kept and the
    kit copy is written as a `<rel>.kit-<version>` sidecar; a partial file with no
    managed block gets the kit block appended; one with a block is spliced to the
    kit's current contract. Writes the marker. Returns a report keyed by
    ADOPT_REPORT_KEYS. Raises FileExistsError if already adopted (use `update`).
    """
    profiles = parse_profiles(profile)
    target = Path(target)
    if read_marker(target) is not None:
        raise FileExistsError(
            f"{target / MARKER_NAME} exists; this repo is already adopted — "
            f"run `standards update` instead."
        )

    src_root = payload_root()
    report: dict[str, list[str]] = {k: [] for k in ADOPT_REPORT_KEYS}
    tracked: dict[str, str] = {}
    managed: dict[str, str] = {}

    for full, rel in iter_payload(src_root, agents):
        cls = classify(rel)
        if cls == "scaffold-once-source":
            continue
        dest = target / rel

        if cls == "kit-tracked":
            if not dest.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(full, dest)
                tracked[rel] = sha256_file(dest)
                report["added"].append(rel)
            elif sha256_file(dest) == sha256_file(full):
                tracked[rel] = sha256_file(dest)
                report["unchanged"].append(rel)
            else:  # adopter owns a differing file — keep it, sidecar the kit copy
                sidecar = target / f"{rel}.kit-{__version__}"
                sidecar.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(full, sidecar)
                tracked[rel] = sha256_file(full)  # baseline; update sees theirs as edited
                report["conflicts"].append(rel)
            continue

        # partial: the kit owns a single managed block; the rest is the adopter's.
        src_text = full.read_text(encoding="utf-8")
        src_inner = _require_block(src_text, rel).inner
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(full, dest)
            managed[rel] = _require_hash(dest.read_text(encoding="utf-8"), rel)
            report["added"].append(rel)
            continue
        cur_text = dest.read_text(encoding="utf-8")
        cur_block = find_block(cur_text)
        if cur_block is not None:  # has our block already — install the current contract
            if cur_block.inner == src_inner:
                report["unchanged"].append(rel)
            else:
                dest.write_text(splice_block(cur_text, src_inner), encoding="utf-8")
                report["spliced"].append(rel)
            managed[rel] = _require_hash(dest.read_text(encoding="utf-8"), rel)
        elif not has_begin_marker(cur_text):  # plain file — append the kit block
            kit_block = extract_block(src_text)
            if kit_block is None:
                raise ValueError(f"{rel}: expected exactly one kit-managed block, found none")
            dest.write_text(cur_text.rstrip("\n") + "\n\n" + kit_block + "\n",
                            encoding="utf-8")
            managed[rel] = _require_hash(dest.read_text(encoding="utf-8"), rel)
            report["spliced"].append(rel)
        else:  # malformed/duplicate markers — don't guess, sidecar
            sidecar = target / f"{rel}.kit-{__version__}"
            sidecar.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(full, sidecar)
            report["conflicts"].append(rel)

    report["scaffolded"] = _seed_scaffold_once(target, src_root, profiles=profiles,
                                               adopted=adopted)
    if _point_checklist(target, profiles):  # the adopter's checklist, kept but re-pointed
        report["spliced"].append(CHECKLIST)

    write_marker(target, kit_version=__version__, profile=profiles,
                 adopted=adopted, tracked=tracked, managed=managed,
                 keep={**NEW_ADOPTION_KEYS, "agents": list(agents)})
    return report
