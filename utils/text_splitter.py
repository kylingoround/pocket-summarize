"""Utility functions for splitting large transcripts into manageable chunks."""
import re
from typing import List

DEFAULT_MAX_CHARS_PER_CHUNK = 4000


def split_text_into_chunks(text: str, max_chars: int = DEFAULT_MAX_CHARS_PER_CHUNK) -> List[str]:
    """Split a transcript into sentence-aligned chunks below ``max_chars`` characters.

    Args:
        text: Full transcript string.
        max_chars: Maximum number of characters allowed in each chunk.

    Returns:
        A list of transcript chunks each no longer than ``max_chars`` characters.
    """
    if not text:
        return []

    normalized_text = re.sub(r"\s+", " ", text).strip()
    if not normalized_text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", normalized_text)

    chunks: List[str] = []
    current_chunk = ""

    for sentence in sentences:
        if not sentence:
            continue

        sentence = sentence.strip()

        if len(sentence) > max_chars:
            # Flush current chunk before handling the oversized sentence.
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""

            # Break the long sentence into slices.
            for start in range(0, len(sentence), max_chars):
                piece = sentence[start:start + max_chars]
                chunks.append(piece)
            continue

        tentative_chunk = f"{current_chunk} {sentence}".strip() if current_chunk else sentence
        if len(tentative_chunk) > max_chars:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence
        else:
            current_chunk = tentative_chunk

    if current_chunk:
        chunks.append(current_chunk)

    cleaned_chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    for chunk in cleaned_chunks:
        if len(chunk) > max_chars:
            raise ValueError(f"Transcript chunk exceeds max length of {max_chars} characters")

    return cleaned_chunks
