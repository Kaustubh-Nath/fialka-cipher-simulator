"""
Fialka Reflector Module
Handles reflector pass and optional Magic Circuit (Dreipunktschaltung) mappings.
"""

from config import DEFAULT_REFLECTOR_PAIRS, ALPHABET_SIZE

class Reflector:
    """Manages the Reflector (Umkehrwalze) stage."""

    def __init__(self, pairs: list[tuple[int, int]] = None):
        if pairs is None:
            pairs = DEFAULT_REFLECTOR_PAIRS
        self.map = self._build_map(pairs)

    def _build_map(self, pairs: list[tuple[int, int]]) -> list[int]:
        mapping = [0] * ALPHABET_SIZE
        for a, b in pairs:
            mapping[a] = b
            mapping[b] = a
        return mapping

    def reflect(self, signal: int) -> int:
        """Passes electrical signal through reflector matrix."""
        return self.map[signal]
