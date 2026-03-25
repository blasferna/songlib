"""
ChordPro parsing, transposition, and notation conversion utilities.

ChordPro format embeds chords inline with lyrics:
    [Am]Amazing [G]grace, how [C]sweet the [Am]sound

This module provides functions to:
- Parse ChordPro text into structured segments
- Strip chords for lyrics-only display
- Transpose chords between keys
- Convert between English (C, D, E…) and Latin (Do, Re, Mi…) notation
"""

import re

# Chromatic scales
ENGLISH_NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
LATIN_NOTES = [
    "Do",
    "Do#",
    "Re",
    "Re#",
    "Mi",
    "Fa",
    "Fa#",
    "Sol",
    "Sol#",
    "La",
    "La#",
    "Si",
]

# Flat → sharp mappings (normalisation)
FLAT_TO_SHARP = {
    "Db": "C#",
    "Eb": "D#",
    "Fb": "E",
    "Gb": "F#",
    "Ab": "G#",
    "Bb": "A#",
    "Cb": "B",
    # Latin flats
    "Reb": "Do#",
    "Mib": "Re#",
    "Fab": "Mi",
    "Solb": "Fa#",
    "Lab": "Sol#",
    "Sib": "La#",
    "Dob": "Si",
}

# Build lookup: note name → index in chromatic scale
_ENGLISH_INDEX = {note: i for i, note in enumerate(ENGLISH_NOTES)}
_LATIN_INDEX = {note: i for i, note in enumerate(LATIN_NOTES)}

# Also index the flat names
for flat, sharp in FLAT_TO_SHARP.items():
    if sharp in _ENGLISH_INDEX:
        _ENGLISH_INDEX[flat] = _ENGLISH_INDEX[sharp]
    if sharp in _LATIN_INDEX:
        _LATIN_INDEX[flat] = _LATIN_INDEX[sharp]

# Merge into a single lookup
_NOTE_INDEX = {**_ENGLISH_INDEX, **_LATIN_INDEX}

# Regex to match a chord token inside [ ]
_CHORD_RE = re.compile(r"\[([^\]]+)\]")

# Regex to split a chord into root + suffix.
# Matches English roots (A-G with optional # or b) and Latin roots.
_ROOT_RE = re.compile(
    r"^(Do#?|Dob?|Re#?|Reb?|Mi#?|Fa#?|Sol#?|Solb?|Lab?|La#?|Sib?|Si"
    r"|[A-G][#b]?)"
    r"(.*)$",
    re.IGNORECASE,
)


def _normalise_root(root):
    """Normalise a root note: title-case, resolve flats to sharps."""
    # Title-case: first letter upper, rest lower — but handle Sol specially
    if root.lower().startswith("sol"):
        root = "Sol" + root[3:]
    elif root.lower().startswith("do"):
        root = "Do" + root[2:]
    elif root.lower().startswith("re"):
        root = "Re" + root[2:]
    elif root.lower().startswith("mi"):
        root = "Mi" + root[2:]
    elif root.lower().startswith("fa"):
        root = "Fa" + root[2:]
    elif root.lower().startswith("la"):
        root = "La" + root[2:]
    elif root.lower().startswith("si"):
        root = "Si" + root[2:]
    else:
        root = root[0].upper() + root[1:]

    # Resolve flats
    if root in FLAT_TO_SHARP:
        root = FLAT_TO_SHARP[root]

    return root


def _split_chord(chord_name):
    """Split a chord into (root, suffix). E.g. 'Am7' → ('A', 'm7'), 'Do#m' → ('Do#', 'm')."""
    m = _ROOT_RE.match(chord_name)
    if not m:
        return None, chord_name
    root = _normalise_root(m.group(1))
    suffix = m.group(2)
    return root, suffix


def calculate_semitones(from_key, to_key):
    """Calculate the number of semitones between two keys.

    Args:
        from_key: Source key, e.g. "Am", "C", "Do"
        to_key: Target key, e.g. "Cm", "G", "Sol"

    Returns:
        Integer number of semitones (can be negative).
    """
    from_root, _ = _split_chord(from_key)
    to_root, _ = _split_chord(to_key)

    if from_root is None or to_root is None:
        return 0

    from_idx = _NOTE_INDEX.get(from_root)
    to_idx = _NOTE_INDEX.get(to_root)

    if from_idx is None or to_idx is None:
        return 0

    return (to_idx - from_idx) % 12


def transpose_chord(chord_name, semitones):
    """Transpose a chord by N semitones.

    Args:
        chord_name: Full chord name, e.g. "Am7", "C#dim"
        semitones: Number of semitones to shift (positive = up)

    Returns:
        Transposed chord name with the same suffix.
    """
    if semitones == 0:
        return chord_name

    root, suffix = _split_chord(chord_name)
    if root is None:
        return chord_name

    idx = _NOTE_INDEX.get(root)
    if idx is None:
        return chord_name

    new_idx = (idx + semitones) % 12

    # Determine if the root was english or latin
    if root in _ENGLISH_INDEX:
        new_root = ENGLISH_NOTES[new_idx]
    else:
        new_root = LATIN_NOTES[new_idx]

    return new_root + suffix


def convert_notation(chord_name, target_notation):
    """Convert a chord's root between English and Latin notation.

    Args:
        chord_name: Full chord name, e.g. "Am7", "Do#m"
        target_notation: "english" or "latin"

    Returns:
        Chord name with root converted to the target notation.
    """
    root, suffix = _split_chord(chord_name)
    if root is None:
        return chord_name

    idx = _NOTE_INDEX.get(root)
    if idx is None:
        return chord_name

    if target_notation == "latin":
        new_root = LATIN_NOTES[idx]
    else:
        new_root = ENGLISH_NOTES[idx]

    return new_root + suffix


def strip_chords(text):
    """Remove all chord annotations from ChordPro text, returning clean lyrics.

    Args:
        text: ChordPro formatted text, e.g. "[Am]Amazing [G]grace"

    Returns:
        Plain lyrics text, e.g. "Amazing grace"
    """
    if not text:
        return ""
    return _CHORD_RE.sub("", text)


def parse_chordpro(text):
    """Parse ChordPro text into structured line data.

    Args:
        text: ChordPro formatted text

    Returns:
        List of lines, where each line is a list of segments:
        [{"chord": "Am" or None, "text": "Amazing "}]
    """
    if not text:
        return []

    result = []
    for line in text.split("\n"):
        segments = []
        pos = 0
        for match in _CHORD_RE.finditer(line):
            # Text before this chord (with no chord above it)
            if match.start() > pos:
                segments.append({"chord": None, "text": line[pos : match.start()]})
            # Find the text that follows this chord until the next chord or end of line
            chord = match.group(1)
            text_start = match.end()
            # Look for next chord marker
            next_match = _CHORD_RE.search(line, text_start)
            if next_match:
                text_after = line[text_start : next_match.start()]
            else:
                text_after = line[text_start:]
            segments.append({"chord": chord, "text": text_after})
            pos = next_match.start() if next_match else len(line)

        # If no chords found in this line, the whole line is text
        if not segments:
            segments.append({"chord": None, "text": line})

        result.append(segments)

    return result


def process_chordpro(text, original_key="", target_key="", notation="english"):
    """Full pipeline: parse ChordPro → transpose → convert notation.

    Args:
        text: ChordPro formatted text
        original_key: The key the song was written in (e.g. "Am")
        target_key: The key to transpose to (e.g. "Cm")
        notation: "english" or "latin"

    Returns:
        List of lines, each a list of segments with transposed/converted chords:
        [{"chord": "Lam" or None, "text": "Amazing "}]
    """
    lines = parse_chordpro(text)

    semitones = 0
    if original_key and target_key:
        semitones = calculate_semitones(original_key, target_key)

    for line in lines:
        for segment in line:
            if segment["chord"] is not None:
                chord = segment["chord"]
                if semitones:
                    chord = transpose_chord(chord, semitones)
                if notation != "english":
                    chord = convert_notation(chord, notation)
                segment["chord"] = chord

    return lines
