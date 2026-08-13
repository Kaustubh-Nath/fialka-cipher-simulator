"""
Fialka Rotors Module
Defines Rotor wiring specifications, rotation positions, and stepping logic.
"""

from config import ALPHABET_SIZE

def _generate_deterministic_permutation(seed: int) -> list[int]:
    """Generates a reproducible 50-contact permutation for a given seed."""
    arr = list(range(ALPHABET_SIZE))
    m = ALPHABET_SIZE
    s = seed
    while m > 0:
        s = (s * 9301 + 49297) % 233280
        i = int((s / 233280) * m)
        m -= 1
        arr[m], arr[i] = arr[i], arr[m]
    return arr

# Library of 10 Rotors (Each has 50 contacts, wired 0-49)
HISTORICAL_ROTORS = [
    {"id": 1,  "name": "Rotor I",   "wiring": _generate_deterministic_permutation(101)},
    {"id": 2,  "name": "Rotor II",  "wiring": _generate_deterministic_permutation(202)},
    {"id": 3,  "name": "Rotor III", "wiring": _generate_deterministic_permutation(303)},
    {"id": 4,  "name": "Rotor IV",  "wiring": _generate_deterministic_permutation(404)},
    {"id": 5,  "name": "Rotor V",   "wiring": _generate_deterministic_permutation(505)},
    {"id": 6,  "name": "Rotor VI",  "wiring": _generate_deterministic_permutation(606)},
    {"id": 7,  "name": "Rotor VII", "wiring": _generate_deterministic_permutation(707)},
    {"id": 8,  "name": "Rotor VIII","wiring": _generate_deterministic_permutation(808)},
    {"id": 9,  "name": "Rotor IX",  "wiring": _generate_deterministic_permutation(909)},
    {"id": 10, "name": "Rotor X",   "wiring": _generate_deterministic_permutation(1010)},
]


class RotorBank:
    """Manages the 10-Rotor Assembly Bank, positions, and stepping mechanics."""

    def __init__(self, rotor_order: list[int] = None, positions: list[int] = None):
        self.rotor_order = rotor_order if rotor_order else list(range(10))
        self.positions = positions if positions else [0] * 10

    def step_rotors(self) -> list[int]:
        """Steps rotors using standard odometer carry propagation."""
        stepped_slots = []
        for slot in range(9, -1, -1):
            self.positions[slot] = (self.positions[slot] + 1) % ALPHABET_SIZE
            stepped_slots.append(slot)
            if self.positions[slot] != 0:
                break # Stop carry propagation if no overflow
        return stepped_slots

    def get_wiring(self, slot_index: int) -> list[int]:
        """Returns the 50-contact wiring array for a given rotor slot."""
        rotor_idx = self.rotor_order[slot_index]
        return HISTORICAL_ROTORS[rotor_idx]["wiring"]

    def set_position_by_char(self, slot_index: int, char: str, alphabet: list[str]) -> bool:
        """Sets rotor position directly using a character (e.g. 'K')."""
        char_upper = char.upper()
        if char_upper in alphabet:
            self.positions[slot_index] = alphabet.index(char_upper)
            return True
        return False

    def set_position_by_num(self, slot_index: int, pos: int):
        """Sets rotor position directly using a number (0-49)."""
        self.positions[slot_index] = pos % ALPHABET_SIZE
