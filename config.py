"""
Fialka Configuration Module
Defines Alphabets, Reflector Mappings, and Presets.
Easily customizable.
"""

# 50-Contact Alphabet Set: A-Z (26), 0-9 (10), Punctuation & Symbols (14)
ALPHABET = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y', 'Z',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    '.', ',', '-', '?', '!', ':', ';', '/', '+', '=', '*', '@', '#', ' '
]

ALPHABET_SIZE = len(ALPHABET) # 50 contacts

# Default Reflector Pairs (Connects contact i with i + 25)
DEFAULT_REFLECTOR_PAIRS = [(i, i + 25) for i in range(25)]

# Presets Configuration
PRESETS = {
    "default": {
        "description": "Standard Rotor Setup (Order: 1 to 10, Positions: All 0)",
        "rotor_order": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        "positions": [0] * 10
    },
    "alternate": {
        "description": "Staggered Starting Positions & Order",
        "rotor_order": [5, 6, 7, 8, 9, 0, 1, 2, 3, 4],
        "positions": [5, 10, 15, 20, 25, 30, 35, 40, 45, 12]
    }
}
