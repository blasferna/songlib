from django.test import TestCase

from app.chords import (
    split_chord_lines_into_slides,
    split_lyrics_into_slides,
    split_lyrics_into_stanzas,
)


class SplitLyricsIntoSlidesTests(TestCase):
    def test_empty_text(self):
        self.assertEqual(split_lyrics_into_slides(""), [])
        self.assertEqual(split_lyrics_into_slides("   \n  "), [])

    def test_stanza_breaks(self):
        text = "Line one\nLine two\n\nLine three"
        self.assertEqual(
            split_lyrics_into_stanzas(text),
            [["Line one", "Line two"], ["Line three"]],
        )
        self.assertEqual(
            split_lyrics_into_slides(text),
            [["Line one", "Line two"], ["Line three"]],
        )

    def test_long_stanza_stays_together_by_default(self):
        text = "A\nB\nC\nD\nE"
        self.assertEqual(
            split_lyrics_into_slides(text),
            [["A", "B", "C", "D", "E"]],
        )

    def test_long_stanza_splits_at_max_lines(self):
        text = "A\nB\nC\nD\nE"
        self.assertEqual(
            split_lyrics_into_slides(text, max_lines=4),
            [["A", "B", "C", "D"], ["E"]],
        )

    def test_chord_lines_follow_same_structure(self):
        plain = "Verse one\n\nChorus line"
        chord_lines = [
            [{"chord": "C", "text": "Verse one"}],
            [{"chord": None, "text": ""}],
            [{"chord": "G", "text": "Chorus line"}],
        ]
        plain_slides = split_lyrics_into_slides(plain)
        chord_slides = split_chord_lines_into_slides(chord_lines)
        self.assertEqual(len(plain_slides), len(chord_slides))
        self.assertEqual(len(plain_slides[0]), len(chord_slides[0]))
