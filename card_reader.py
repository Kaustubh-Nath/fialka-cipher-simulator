"""
Fialka Card Reader Module (Daily Permutator / Plugboard)
Simulates daily 50-channel punched card permutation layer.
"""

from config import ALPHABET_SIZE

class CardReader:
    """Manages the daily punched card permutator matrix."""

    def __init__(self, permutation: list[int] = None):
        if permutation and len(permutation) == ALPHABET_SIZE:
            self.card = list(permutation)
        else:
            # Identity permutation by default (Channel i -> Channel i)
            self.card = list(range(ALPHABET_SIZE))

    def enter_card(self, channel: int) -> int:
        """Applies punched card channel swap on signal entry."""
        return self.card[channel]

    def exit_card(self, channel: int) -> int:
        """Applies inverse punched card channel swap on signal exit."""
        # Build inverse card mapping
        inv_card = [0] * ALPHABET_SIZE
        for i, val in enumerate(self.card):
            inv_card[val] = i
        return inv_card[channel]
