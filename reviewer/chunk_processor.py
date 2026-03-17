CHUNK_SIZE = 100  # lines per chunk sent to the LLM


def split_patch_into_chunks(patch: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """
    Split a large diff patch into smaller chunks so we never exceed LLM context limits.
    Each chunk tries to break at hunk boundaries (@@ lines) when possible.
    Returns a list of patch string chunks.
    """
    lines = patch.splitlines(keepends=True)

    if len(lines) <= chunk_size:
        # Small enough — no splitting needed
        return [patch]

    chunks = []
    current_chunk: list[str] = []
    current_size = 0

    for line in lines:
        current_chunk.append(line)
        current_size += 1

        # Prefer to break at hunk headers so each chunk is a valid diff fragment
        at_hunk_boundary = line.startswith("@@") and current_size > 1
        at_size_limit = current_size >= chunk_size

        if at_size_limit or (at_hunk_boundary and current_size >= chunk_size // 2):
            chunks.append("".join(current_chunk))
            current_chunk = []
            current_size = 0

    if current_chunk:
        chunks.append("".join(current_chunk))

    return chunks


def adjust_line_numbers(comments: list[dict], chunk_index: int, chunk_size: int) -> list[dict]:
    """
    When a diff is split into chunks, line numbers reported by the LLM are relative
    to the chunk. This function shifts them back to the absolute line number in the
    full diff so GitHub inline comments land on the right line.
    """
    offset = chunk_index * chunk_size
    adjusted = []
    for c in comments:
        c = c.copy()
        c["line"] = c["line"] + offset
        adjusted.append(c)
    return adjusted
