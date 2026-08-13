"""
Fialka Core Engine Module
Orchestrates Forward Pass -> Reflector Pass -> Reverse Pass -> Stepping.
"""

from config import ALPHABET, ALPHABET_SIZE
from rotors import RotorBank
from reflector import Reflector
from card_reader import CardReader

class FialkaEngine:
    """Master Cryptographic Engine for Fialka 10-Rotor Cipher."""

    def __init__(self):
        self.alphabet = ALPHABET
        self.rotors = RotorBank()
        self.reflector = Reflector()
        self.card_reader = CardReader()

    # --- EXPLICIT PASS STAGE 1: FORWARD PASS ---
    def forward_pass(self, signal: int) -> tuple[int, list[dict]]:
        """Traces signal Right-to-Left through 10 Rotors (Slot 9 down to 0)."""
        current_signal = signal
        forward_trace = []

        for slot in range(9, -1, -1):
            pos = self.rotors.positions[slot]
            wiring = self.rotors.get_wiring(slot)

            contact_in = (current_signal + pos) % ALPHABET_SIZE
            wire_out = wiring[contact_in]
            contact_out = (wire_out - pos + ALPHABET_SIZE) % ALPHABET_SIZE

            forward_trace.append({
                "slot": slot,
                "position": pos,
                "contact_in": contact_in,
                "wire_out": wire_out,
                "contact_out": contact_out
            })

            current_signal = contact_out

        return current_signal, forward_trace

    # --- EXPLICIT PASS STAGE 2: REFLECTOR PASS ---
    def reflector_pass(self, signal: int) -> int:
        """Passes signal through Reflector."""
        return self.reflector.reflect(signal)

    # --- EXPLICIT PASS STAGE 3: REVERSE PASS ---
    def reverse_pass(self, signal: int) -> tuple[int, list[dict]]:
        """Traces signal Left-to-Right back through 10 Rotors (Slot 0 up to 9)."""
        current_signal = signal
        reverse_trace = []

        for slot in range(0, 10):
            pos = self.rotors.positions[slot]
            wiring = self.rotors.get_wiring(slot)

            contact_in = (current_signal + pos) % ALPHABET_SIZE
            
            # Inverse wiring lookup
            wire_out = wiring.index(contact_in)
            contact_out = (wire_out - pos + ALPHABET_SIZE) % ALPHABET_SIZE

            reverse_trace.append({
                "slot": slot,
                "position": pos,
                "contact_in": contact_in,
                "wire_out": wire_out,
                "contact_out": contact_out
            })

            current_signal = contact_out

        return current_signal, reverse_trace

    # --- COMPLETE SINGLE CHARACTER ENCIPHERMENT CYCLE ---
    def encipher_char(self, char: str) -> dict:
        """
        Executes single character encipherment flow:
        Card Entry -> Forward Rotors -> Reflector -> Reverse Rotors -> Card Exit -> Step Rotors
        """
        upper_char = char.upper()
        if upper_char not in self.alphabet:
            return {"input_char": char, "output_char": char, "is_ignored": True}

        input_index = self.alphabet.index(upper_char)

        # 1. Card Reader Entry Pass
        card_entry_signal = self.card_reader.enter_card(input_index)

        # 2. Forward Rotors Pass (9 -> 0)
        reflector_entry_signal, fwd_trace = self.forward_pass(card_entry_signal)

        # 3. Reflector Pass
        reflector_exit_signal = self.reflector_pass(reflector_entry_signal)

        # 4. Reverse Rotors Pass (0 -> 9)
        card_exit_signal, rev_trace = self.reverse_pass(reflector_exit_signal)

        # 5. Card Reader Exit Pass
        final_output_index = self.card_reader.exit_card(card_exit_signal)
        output_char = self.alphabet[final_output_index]

        # 6. Step Rotors After Encipherment Cycle
        stepped_slots = self.rotors.step_rotors()

        return {
            "input_char": upper_char,
            "input_index": input_index,
            "card_entry_signal": card_entry_signal,
            "forward_trace": fwd_trace,
            "reflector_entry": reflector_entry_signal,
            "reflector_exit": reflector_exit_signal,
            "reverse_trace": rev_trace,
            "card_exit_signal": card_exit_signal,
            "output_index": final_output_index,
            "output_char": output_char,
            "stepped_slots": stepped_slots,
            "is_ignored": False
        }

    def process_text(self, text: str) -> tuple[str, list[dict]]:
        """Enciphers or deciphers an entire text block."""
        result_chars = []
        traces = []
        for char in text:
            res = self.encipher_char(char)
            result_chars.append(res["output_char"])
            if not res["is_ignored"]:
                traces.append(res)
        return "".join(result_chars), traces

    def reset_positions(self):
        """Resets all rotor positions back to zero."""
        self.rotors.positions = [0] * 10
