"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


PARAGRAPH_BREAK = re.compile(r"\n\s*\n")


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split on paragraph breaks, and keep the document's title line on every piece.

    Every post in `campus_life` is a title line, a blank line, then two or three
    paragraphs that answer different questions. `housing_aldridge_hall_laundry`
    says what the machines cost in one paragraph and when to avoid the queue in
    the next; those are two questions, so they are two chunks.

    The title goes back onto each piece because the posts are near-duplicates of
    one another — eight dining halls and eight residence buildings written to the
    same template. On its own, "Best time to do laundry here is Tuesday" doesn't
    say which building "here" is, and there are seven other buildings it could
    plausibly be retrieved for.

    A character count can't see any of that. It cuts 12 of the 88 posts and
    leaves the rest alone, and where it does cut it lands mid-sentence.
    """
    chunks: list[Chunk] = []

    for doc in documents:
        blocks = [b.strip() for b in PARAGRAPH_BREAK.split(doc.text) if b.strip()]
        if not blocks:
            continue

        title, bodies = blocks[0], blocks[1:]

        # A document with nothing under its title is still one chunk — better a
        # short chunk than a dropped document.
        pieces = [f"{title}\n\n{body}" for body in bodies] or [title]

        index = 0
        for piece in pieces:
            # No paragraph in this corpus comes close to a full window, but
            # other corpora have long ones. Rather than emit a single enormous
            # chunk, hand those back to the fixed-size splitter.
            if len(piece) > config.CHUNK_SIZE:
                parts = [
                    c.text
                    for c in fallback_split([Document(source=doc.source, text=piece)])
                ]
            else:
                parts = [piece]

            for part in parts:
                chunks.append(
                    Chunk(
                        text=part,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::split_documents",
                    )
                )
                index += 1

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
