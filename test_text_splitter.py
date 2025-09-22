import unittest

from utils.text_splitter import split_text_into_chunks
from nodes import MAX_TOPIC_CONTEXT_CHARS, build_topic_context


class TextSplitterTestCase(unittest.TestCase):
    def test_split_text_into_chunks_respects_limit(self):
        text = "Sentence one. " * 1000
        max_chars = 120
        chunks = split_text_into_chunks(text, max_chars=max_chars)
        self.assertTrue(chunks)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), max_chars)

    def test_build_topic_context_with_matching_chunks(self):
        chunks = [
            "Introductory content about setup.",
            "Deep dive into machine learning models and their applications.",
            "Closing remarks and summary."
        ]
        context = build_topic_context("machine learning", chunks)
        self.assertIn("machine learning", context.lower())
        self.assertLessEqual(len(context), MAX_TOPIC_CONTEXT_CHARS)

    def test_build_topic_context_raises_for_oversized_chunk(self):
        oversized_chunk = "a" * (MAX_TOPIC_CONTEXT_CHARS + 5)
        with self.assertRaises(ValueError):
            build_topic_context("test", [oversized_chunk])


if __name__ == "__main__":
    unittest.main()
