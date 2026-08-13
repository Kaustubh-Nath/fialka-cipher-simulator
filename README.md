# 🔐 FIALKA М-125 (EXTENDED) — 10-Rotor Cipher Simulator

An interactive, web-based cryptographic simulator and live signal tracer for the Cold War-era Soviet **Fialka M-125 10-Rotor Cipher Machine**.

[![Live Demo](https://img.shields.io/badge/Render-Live%20Demo-brightgreen?logo=render&logoColor=white)](YOUR_RENDER_LIVE_URL_HERE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌐 Live Application

The project is deployed and live on Render:  
👉 **[Launch Fialka M-125 Simulator]((https://fialka-cipher-simulator.onrender.com/))**

---

## 🌟 Overview

The Fialka M-125 was a highly secure electro-mechanical cipher machine utilized by the Soviet Union and Warsaw Pact forces. Operating on 10 interchangeable rotors with 50 electrical contacts each (A-Z, 0-9, and punctuation symbols), a punched card permutator layer, and a reflector, it was far more complex than the WWII German Enigma machine.

This web application simulates the exact cryptographic signal path through all 10 rotor layers, daily punched card permutators, and reflector bounces in real time.

---

## ✨ Key Features

- ⚙️ **10-Rotor Assembly Bank:** Real-time rotor configuration with 50 contacts ($00 - 49$). Supports mouse stepping, arrow keys, and direct numpad input.
- ⚡ **Live SVG Electrical Circuit Tracer:** Visualizes the character signal path—a solid green line tracing the **Forward Pass** ($10 \rightarrow 1$) into the reflector, and a dashed amber line tracing the **Return Pass** ($1 \rightarrow 10$).
- 🎛️ **Key Presets & State Persistence:** Quickly apply standard key setups, save custom rotor configurations, or reset machine states.
- 💬 **Batch Message Processing:** Encipher or decipher text blocks instantaneously with dual input/output console controls.
- 🐍 **Pure Python Backend:** Core cipher execution, permutation passes, and odometer rotor stepping logic are managed cleanly via a lightweight Python server.

---

## 📸 Interface Layout

The web application features a dark-themed command-center layout:
1. **Header & Key Presets** (Top): Quick key setups, preset loader, and machine reset.
2. **10-Rotor Assembly Bank**: Configurable rotor selections, position inputs, and step dials.
3. **Batch Message Processing**: Dual text console for fast message encipherment/decipherment.
4. **Live Electrical Circuit Tracer** (Bottom): Dynamic 2D SVG vector graph showing green forward and amber return signal pathways.

---

## 📁 Project Structure

```text
.
├── web_server.py           # Threading HTTP server & REST API endpoint router
├── engine.py               # Core cryptographic orchestrator (Fwd -> Refl -> Rev -> Step)
├── rotors.py               # 10-Rotor bank, wiring permutations, and odometer logic
├── card_reader.py          # Daily 50-channel punched card permutator
├── reflector.py            # Umkehrwalze reflector bounce mapping
├── config.py               # 50-contact alphabet definition & key presets
├── configuration_manager.py# JSON configuration save/load manager
├── index.html              # Dashboard UI structure & SVG container
├── style.css               # Dark theme command-center stylesheet
├── script.js               # Async API controller & SVG vector tracer renderer
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
