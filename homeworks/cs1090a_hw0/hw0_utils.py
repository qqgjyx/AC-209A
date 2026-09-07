"""Helpers shipped with CS1090A Homework 0.

Two audiences, one file:

* **Students.** Part 2 of HW0 is a chain -- each question consumes the previous
  question's output. So after every question the notebook calls one of the
  ``canonical_*`` functions below and hands you back a known-good value to carry
  forward. A wrong answer in Q2.2 costs you Q2.2 and nothing else.

  These functions are reference implementations. You can read them. HW0 is graded
  on completion, so there is nothing to be gained by copying them -- but the
  diagnostic you get back is built from what you actually wrote, so a copied
  answer buys you a report about somebody who isn't you. Use ``compare()`` to
  find out where your version differs; that is the part worth your time.

* **The autograder.** ``grading/autograder/`` imports this same module as its
  reference, so the notebook and the grader can never disagree about what the
  right answer is.

Run this file directly to re-verify every pinned constant against the corpus::

    python3 hw0_utils.py
"""

from __future__ import annotations

import re
from pathlib import Path

# --------------------------------------------------------------------------
# The corpus
# --------------------------------------------------------------------------

DATA_FILE = "pg12242.txt"

#: Every preface in the compilation opens with this line.
PREFACE_MARKER = "POEMS\n"
#: The first numbered poem after a preface. Marks where the poetry starts.
FIRST_POEM_MARKER = "I. "
#: The Project Gutenberg license block that closes the file.
LICENSE_MARKER = "End of Project Gutenberg"

#: How many newlines separate two consecutive poems.
POEM_SEPARATOR = "\n" * 6

#: Characters that may appear in the roman numerals this corpus actually uses.
#: C and D are deliberately absent -- including them would make ``DID.`` and
#: ``COME.`` look like numerals and delete real poem lines. The largest numeral
#: in the text is well under 100, so nothing is lost.
ROMAN_CHARS = frozenset("IVXLM")


def load_text(path: str | Path | None = None) -> str:
    """Read the Dickinson compilation and return it as one string."""
    if path is None:
        path = Path(__file__).resolve().parent / "data" / DATA_FILE
    return Path(path).read_text(encoding="utf-8")


# --------------------------------------------------------------------------
# Q2.2 -- locating each series
# --------------------------------------------------------------------------


def series_bounds(s: str, search_from: int = 0) -> tuple[int, int]:
    """Return ``(start, end)`` of the next series' poem block at or after ``search_from``.

    ``start`` is the index of the first numbered poem following the next
    preface. ``end`` is the index of the preface after that -- or, for the last
    series, the index of the Project Gutenberg license.

    Ex:
        series_bounds(text) -> (6714, 49215)
    """
    preface = s.index(PREFACE_MARKER, search_from)
    start = s.index(FIRST_POEM_MARKER, preface)

    end = s.find(PREFACE_MARKER, start)
    if end == -1:
        end = s.index(LICENSE_MARKER, start)
    return start, end


def canonical_series(text: str) -> tuple[str, str, str]:
    """Return the three series' poem blocks, stripped of surrounding whitespace."""
    out = []
    position = 0
    for _ in range(3):
        start, end = series_bounds(text, position)
        out.append(text[start:end].strip())
        position = end
    return tuple(out)  # type: ignore[return-value]


# --------------------------------------------------------------------------
# Q2.2 cleanup (provided, not asked) -- the one editor annotation
# --------------------------------------------------------------------------


def canonical_poems_text(text: str) -> str:
    """The three series joined, with the single bracketed editor note removed.

    Exactly one square-bracketed annotation appears in the corpus, under the
    first poem. It and the blank line beneath it come out here so that no
    question has to special-case it.
    """
    joined = POEM_SEPARATOR.join(canonical_series(text))
    open_idx = joined.index("[")
    close_idx = joined.index("]")

    # Exactly one newline on each side, not rstrip/lstrip: the annotation sits
    # between a title and its poem, and greedily eating newlines would weld
    # "SUCCESS." onto "Success is counted sweetest".
    before = joined[:open_idx].removesuffix("\n")
    after = joined[close_idx + 1 :].removeprefix("\n")
    return before + after


# --------------------------------------------------------------------------
# Q2.3 -- section titles and poem numbers
# --------------------------------------------------------------------------


def startswith_roman(line: str) -> bool:
    """True if ``line``'s first whitespace-delimited token is a roman numeral.

    A token qualifies when it ends in ``.``, has a non-empty stem, and every
    character of that stem is one of I, V, X, L, M.

    Ex:
        startswith_roman("III. NATURE.")            -> True
        startswith_roman("I'm nobody! Who are you?") -> False
    """
    tokens = line.split()
    if not tokens:
        return False

    token = tokens[0]
    if not token.endswith("."):
        return False

    stem = token[:-1]
    # An empty stem must not qualify: all([]) is True, which is how the 2025
    # version came to treat a line beginning "." as a numeral.
    return bool(stem) and all(char in ROMAN_CHARS for char in stem)


def canonical_poems_text_nonum(text: str) -> str:
    """``canonical_poems_text`` with every roman-numeral line removed."""
    kept = [
        line
        for line in canonical_poems_text(text).split("\n")
        if not startswith_roman(line)
    ]
    return "\n".join(kept).strip()


# --------------------------------------------------------------------------
# Q2.4 -- one string per poem
# --------------------------------------------------------------------------


def canonical_poem_list(text: str) -> list[str]:
    """Split the cleaned text into a list of poems, longest-first order preserved."""
    parts = canonical_poems_text_nonum(text).split(POEM_SEPARATOR)
    return [part.strip() for part in parts if part.strip()]


# --------------------------------------------------------------------------
# Q2.5 -- first line -> poem
# --------------------------------------------------------------------------


def has_editor_title(poem: str) -> bool:
    """True if this poem carries a title the editors added.

    An editor's title is an ALL-CAPS first line. Nothing in Dickinson's verse is
    all-caps, so the test is exact on this corpus: it finds 249 titles and no false
    positives. Requiring a trailing "." as well -- the obvious-looking rule -- misses
    ``ALMOST!``, ``WHY?``, ``"TROUBLED ABOUT MANY THINGS."``, ``SAVED!`` and ``WHO?``.
    """
    return first_line(poem).isupper()


def first_line(poem: str) -> str:
    """The poem's first line, title or not."""
    return poem.split("\n")[0]


def canonical_poem_dict(text: str) -> dict[str, str]:
    """Map each poem's opening line to the poem.

    Dickinson titled almost nothing she wrote; the titles in this compilation were
    supplied by her editors after her death, and she is conventionally cited by first
    line instead. So the titles come off and every poem is keyed by the first line of
    its verse.

    That is also why there is no de-duplication here: 445 poems produce 445 distinct
    opening lines, where the editors' titles collided nine times.
    """
    poems: dict[str, str] = {}

    for poem in canonical_poem_list(text):
        body = poem
        if has_editor_title(poem):
            body = poem[len(first_line(poem)) :].lstrip("\n")
        poems[first_line(body)] = body

    return poems


# --------------------------------------------------------------------------
# Q2.6 -- word counts
# --------------------------------------------------------------------------

#: Words are runs of letters, optionally joined by an apostrophe or hyphen, so
#: "old-fashioned" and "I'm" survive intact while trailing punctuation does not.
WORD_RE = re.compile(r"[a-z]+(?:['-][a-z]+)*")

MIN_WORD_LENGTH = 11
MIN_WORD_COUNT = 4


def tokenize(s: str) -> list[str]:
    """Lowercase ``s`` and return its words.

    Ex:
        tokenize("Hope is the thing with feathers--") -> ['hope', 'is', 'the', 'thing', 'with', 'feathers']
    """
    return WORD_RE.findall(s.lower())


def canonical_word_counts(text: str) -> dict[str, int]:
    """How many times each word occurs across every poem body."""
    counts: dict[str, int] = {}
    for body in canonical_poem_dict(text).values():
        for word in tokenize(body):
            counts[word] = counts.get(word, 0) + 1
    return counts


def canonical_top_words(text: str) -> list[str]:
    """Long, frequent words: length >= 11 and at least 4 occurrences.

    Sorted by count descending, ties broken alphabetically ascending. The
    threshold is what makes this well defined -- a plain "top 10" would have to
    choose four winners out of the ten words that tie at three occurrences.
    """
    counts = canonical_word_counts(text)
    hits = [
        word
        for word, n in counts.items()
        if len(word) >= MIN_WORD_LENGTH and n >= MIN_WORD_COUNT
    ]
    return sorted(hits, key=lambda word: (-counts[word], word))


# --------------------------------------------------------------------------
# Checkpoints
# --------------------------------------------------------------------------

_CHECKPOINTS = {
    "series": canonical_series,
    "poems_text": canonical_poems_text,
    "poems_text_nonum": canonical_poems_text_nonum,
    "poem_list": canonical_poem_list,
    "poems_by_first_line": canonical_poem_dict,
    "word_counts": canonical_word_counts,
    "top_words": canonical_top_words,
}


def checkpoint(name: str, text: str):
    """Return the reference value for ``name``, computed from ``text``."""
    if name not in _CHECKPOINTS:
        raise KeyError(f"No checkpoint named {name!r}. Try one of {sorted(_CHECKPOINTS)}.")
    return _CHECKPOINTS[name](text)


def compare(name: str, value, text: str | None = None) -> str:
    """Describe how ``value`` differs from the reference for ``name``.

    Returns a short human-readable report. This never raises and never grades --
    it is here so you can find your own bug.
    """
    if text is None:
        text = load_text()

    try:
        expected = checkpoint(name, text)
    except KeyError as exc:
        return str(exc)

    if value is ... or value is None:
        return f"{name}: not answered yet."

    if type(value) is not type(expected):
        return (
            f"{name}: expected {type(expected).__name__}, "
            f"got {type(value).__name__}."
        )

    if value == expected:
        return f"{name}: matches. ({_describe(expected)})"

    return f"{name}: differs. {_explain(value, expected)}"


def _describe(value) -> str:
    if isinstance(value, str):
        return f"{len(value):,} characters"
    if isinstance(value, (list, tuple)):
        return f"{len(value):,} items"
    if isinstance(value, dict):
        return f"{len(value):,} entries"
    return repr(value)


def _explain(value, expected) -> str:
    if isinstance(expected, str):
        parts = [f"expected {len(expected):,} characters, got {len(value):,}"]
        for i, (got, want) in enumerate(zip(value, expected)):
            if got != want:
                parts.append(
                    f"first difference at index {i}: "
                    f"yours {value[i:i + 30]!r} vs {expected[i:i + 30]!r}"
                )
                break
        return "; ".join(parts) + "."

    if isinstance(expected, (list, tuple)):
        parts = [f"expected {len(expected):,} items, got {len(value):,}"]
        for i, (got, want) in enumerate(zip(value, expected)):
            if got != want:
                parts.append(f"first difference at index {i}: {got!r} vs {want!r}")
                break
        return "; ".join(parts) + "."

    if isinstance(expected, dict):
        missing = sorted(set(expected) - set(value))
        extra = sorted(set(value) - set(expected))
        parts = [f"expected {len(expected):,} entries, got {len(value):,}"]
        if missing:
            parts.append(f"missing {len(missing)} key(s), e.g. {missing[:3]}")
        if extra:
            parts.append(f"{len(extra)} unexpected key(s), e.g. {extra[:3]}")
        if not missing and not extra:
            differing = [k for k in expected if value[k] != expected[k]]
            parts.append(f"same keys, {len(differing)} value(s) differ, e.g. {differing[:3]}")
        return "; ".join(parts) + "."

    return f"expected {expected!r}, got {value!r}."


# --------------------------------------------------------------------------
# Pinned constants -- the release check
# --------------------------------------------------------------------------

EXPECTED = {
    "text_length": 197_438,
    "series_bounds": [(6714, 49215), (55756, 122851), (124616, 177121)],
    "poems_text_nonum_length": 159_426,
    "poem_count": 445,
    "dict_size": 445,
    "editor_titled": 249,
    "first_key": "Success is counted sweetest",
    "last_key": "On this wondrous sea,",
    "top_words": [
        "everlasting",
        "immortality",
        "butterflies",
        "superfluous",
        "countenance",
        "revelations",
    ],
    # The poem the editors called "HOPE.", keyed the way Dickinson is actually cited.
    "hope_key": "Hope is the thing with feathers",
}


def verify(text: str | None = None) -> None:
    """Assert every pinned constant. Raises AssertionError on the first mismatch."""
    if text is None:
        text = load_text()

    assert len(text) == EXPECTED["text_length"], len(text)

    bounds, position = [], 0
    for _ in range(3):
        start, end = series_bounds(text, position)
        bounds.append((start, end))
        position = end
    assert bounds == EXPECTED["series_bounds"], bounds

    nonum = canonical_poems_text_nonum(text)
    assert len(nonum) == EXPECTED["poems_text_nonum_length"], len(nonum)

    poem_list = canonical_poem_list(text)
    assert len(poem_list) == EXPECTED["poem_count"], len(poem_list)

    titled = sum(1 for p in poem_list if has_editor_title(p))
    assert titled == EXPECTED["editor_titled"], titled

    poems = canonical_poem_dict(text)
    assert len(poems) == EXPECTED["dict_size"], len(poems)

    keys = list(poems)
    assert keys[0] == EXPECTED["first_key"], keys[0]
    assert keys[-1] == EXPECTED["last_key"], keys[-1]

    # Every editor's title should have come off: no key survives as ALL CAPS, and no
    # body still opens with the title that was stripped from it.
    left_titled = [k for k in keys if k.isupper()]
    assert not left_titled, left_titled
    assert all(body.startswith(key) for key, body in poems.items())

    assert EXPECTED["hope_key"] in poems, "the poem the editors titled HOPE."

    top = canonical_top_words(text)
    assert top == EXPECTED["top_words"], top

    print(f"corpus              {len(text):,} characters")
    print(f"series bounds       {bounds}")
    print(f"poems_text_nonum    {len(nonum):,} characters")
    print(f"poems               {len(poem_list)} ({titled} carried an editor's title)")
    print(f"dictionary          {len(poems)} keys, all distinct first lines")
    print(f"top_words           {top}")
    print("\nAll pinned constants verified.")


if __name__ == "__main__":
    verify()
