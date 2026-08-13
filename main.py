"""
Fialka Interactive CLI & Test Suite Entrypoint
"""

import sys
from engine import FialkaEngine
from config import PRESETS
from configuration_manager import ConfigurationManager

def print_rotor_bank(engine: FialkaEngine):
    """Prints a clean ASCII display of the 10 rotor slots."""
    slots_str = " | ".join([f"Slot {i+1:<2}" for i in range(10)])
    rotors_str = " | ".join([f"  R{engine.rotors.rotor_order[i]+1:<2} " for i in range(10)])
    pos_num_str = " | ".join([f"  {engine.rotors.positions[i]:02d}  " for i in range(10)])
    pos_chr_str = " | ".join([f"   {engine.alphabet[engine.rotors.positions[i]]}  " for i in range(10)])

    print("\n" + "=" * 80)
    print("                      ROTOR ASSEMBLY BANK (10 ROTORS)")
    print("=" * 80)
    print(f"SLOTS:     {slots_str}")
    print(f"ROTORS:    {rotors_str}")
    print(f"POS (0-49):{pos_num_str}")
    print(f"CHAR:      {pos_chr_str}")
    print("=" * 80 + "\n")

def run_demonstration():
    """Runs automated verification demonstration."""
    print("\n--- FIALKA 10-ROTOR CIPHER DEMONSTRATION ---")
    engine = FialkaEngine()

    plaintext = "SECRET MESSAGE 123! @CONFIDENTIAL#"
    print(f"Original Plaintext:    '{plaintext}'")

    # Encipher message
    ciphertext, traces = engine.process_text(plaintext)
    print(f"Enciphered Ciphertext: '{ciphertext}'")

    # Reset positions to initial state
    engine.reset_positions()

    # Decipher message
    deciphered, _ = engine.process_text(ciphertext)
    print(f"Deciphered Result:     '{deciphered}'")

    # Verify symmetry
    if deciphered == plaintext.upper():
        print("\n[SUCCESS] RECIPROCAL ENCRYPTION VERIFIED: Deciphered text matches Plaintext!")
    else:
        print("\n[FAILED] VERIFICATION FAILED!")

def interactive_shell():
    """Interactive command-line shell mode."""
    engine = FialkaEngine()

    while True:
        print_rotor_bank(engine)
        print("OPTIONS:")
        print("  1. Encipher / Decipher Single Text String")
        print("  2. Change Rotor Position")
        print("  3. Load Key Preset")
        print("  4. Reset Rotor Positions")
        print("  5. Run Automated Symmetry Test")
        print("  6. Save Machine Configuration")
        print("  7. Load Machine Configuration")
        print("  8. Exit")
        choice = input("\nSelect Option (1-8): ").strip()

        if choice == "1":
            text = input("Enter text to process: ").strip()
            if text:
                out_text, traces = engine.process_text(text)
                print(f"\nRESULT: {out_text}")
                if traces:
                    last_trace = traces[-1]
                    print(f"\n[LAST CHARACTER TRACE: '{last_trace['input_char']}' -> '{last_trace['output_char']}']")
                    print(f"  Entry Card Signal:      {last_trace['card_entry_signal']}")
                    print(f"  Reflector Bounce:       Contact {last_trace['reflector_entry']} -> {last_trace['reflector_exit']}")
                    print(f"  Exit Card Signal:       {last_trace['card_exit_signal']}")

        elif choice == "2":
            slot_str = input("Enter Slot Index (1-10): ").strip()
            val_str = input("Enter new Position Number (0-49) or Character (A-Z): ").strip()
            if slot_str.isdigit():
                slot = int(slot_str) - 1
                if 0 <= slot < 10:
                    if val_str.isdigit():
                        engine.rotors.set_position_by_num(slot, int(val_str))
                    else:
                        engine.rotors.set_position_by_char(slot, val_str, engine.alphabet)

        elif choice == "3":
            print("\nAvailable Presets:")
            for k, v in PRESETS.items():
                print(f"  - {k}: {v['description']}")
            p_key = input("Enter preset name: ").strip()
            if p_key in PRESETS:
                engine.rotors.rotor_order = list(PRESETS[p_key]["rotor_order"])
                engine.rotors.positions = list(PRESETS[p_key]["positions"])
                print(f"Applied preset '{p_key}'.")

        elif choice == "4":
            engine.reset_positions()
            print("Rotor positions reset to 00.")

        elif choice == "5":
            run_demonstration()

        elif choice == "6":
            name = input("Configuration name: ").strip()
            if name:
                ConfigurationManager.save(engine, name)

        elif choice == "7":
            configs = ConfigurationManager.list()
            if not configs:
                print("\nNo saved configurations found.")
                continue

            print("\n========== SAVED CONFIGURATIONS ==========")
            for i, config in enumerate(configs, start=1):
                print(f"{i}. {config}")

            selection = input("\nSelect configuration: ").strip()
            if selection.isdigit():
                idx = int(selection) - 1
                if 0 <= idx < len(configs):
                    ConfigurationManager.load(engine, configs[idx])
                else:
                    print("Invalid selection.")
            else:
                print("Invalid input.")

        elif choice == "8":
            print("Exiting Fialka Shell. Goodbye!")
            break
        
if __name__ == "__main__":
    run_demonstration()
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        interactive_shell()
