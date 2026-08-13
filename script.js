class MachineController {
    constructor() {
        this.state = null;
        this.initEventListeners();
        this.loadState();
    }

    async api(url, options = {}) {
        try {
            const response = await fetch(url, options);
            return await response.json();
        } catch (err) {
            console.error("API Error:", err);
            return {};
        }
    }

    async loadState() {
        const data = await this.api("/api/state");
        if (data && data.state) {
            this.state = data.state;
            this.renderRotors();
        }
    }

    initEventListeners() {
        // Process message button
        const processBtn = document.getElementById("process-btn");
        if (processBtn) {
            processBtn.onclick = () => this.processMessage();
        }

        // Reset machine button
        const resetBtn = document.getElementById("reset-btn");
        if (resetBtn) {
            resetBtn.onclick = async () => {
                const data = await this.api("/api/reset", { method: "POST" });
                if (data.state) {
                    this.state = data.state;
                    this.renderRotors();
                    document.getElementById("output-text").value = "";
                    document.getElementById("trace-container").innerHTML = "";
                }
            };
        }

        // Preset dropdown
        const presetSelect = document.getElementById("preset-select");
        if (presetSelect) {
            presetSelect.onchange = async (e) => {
                const presetKey = e.target.value;
                const data = await this.api("/api/preset", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ preset: presetKey })
                });
                if (data.state) {
                    this.state = data.state;
                    this.renderRotors();
                }
            };
        }

        // Copy / Clear button bindings
        const inputBox = document.getElementById("input-text");
        const outputBox = document.getElementById("output-text");

        document.getElementById("copy-input").onclick = () => navigator.clipboard.writeText(inputBox.value);
        document.getElementById("clear-input").onclick = () => { inputBox.value = ""; };
        document.getElementById("copy-output").onclick = () => navigator.clipboard.writeText(outputBox.value);
        document.getElementById("clear-output").onclick = () => { outputBox.value = ""; };
    }

    renderRotors() {
        const container = document.getElementById("rotors-container");
        if (!container || !this.state) return;

        container.innerHTML = "";

        for (let slot = 0; slot < 10; slot++) {
            const currentRotorIdx = this.state.rotor_order[slot];
            const currentPosNum = this.state.positions[slot];
            const currentPosChar = this.state.alphabet[currentPosNum] || "A";

            const card = document.createElement("div");
            card.className = "rotor-card";

            card.innerHTML = `
                <div class="rotor-slot-label">SLOT ${slot + 1}</div>
                <select class="rotor-select" data-slot="${slot}">
                    ${this.state.rotors.map(r => `
                        <option value="${r.id - 1}" ${r.id - 1 === currentRotorIdx ? "selected" : ""}>
                            R${r.id}
                        </option>
                    `).join('')}
                </select>
                <button class="step-btn" data-slot="${slot}" data-dir="up">▲</button>
                <div class="rotor-display">
                    <input type="number" 
                           class="pos-input" 
                           data-slot="${slot}" 
                           min="0" 
                           max="49" 
                           value="${String(currentPosNum).padStart(2, '0')}" 
                           title="Type position (0-49) or use Arrow Up/Down" />
                    <span class="pos-char">${currentPosChar}</span>
                </div>
                <button class="step-btn" data-slot="${slot}" data-dir="down">▼</button>
            `;

            container.appendChild(card);
        }

        // Helper function to update position via API
        const setRotorPosition = async (slot, newPos) => {
            const validPos = (parseInt(newPos, 10) || 0) % 50;
            const data = await this.api("/api/configure", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ slot, position: validPos < 0 ? validPos + 50 : validPos })
            });
            if (data.state) {
                this.state = data.state;
                this.renderRotors();
            }
        };

        // Bind Rotor Select Dropdowns
        container.querySelectorAll(".rotor-select").forEach(select => {
            select.onchange = async (e) => {
                const slot = parseInt(e.target.dataset.slot, 10);
                const rotor = parseInt(e.target.value, 10);
                const data = await this.api("/api/configure", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ slot, rotor })
                });
                if (data.state) {
                    this.state = data.state;
                    this.renderRotors();
                }
            };
        });

        // Bind Numpad / Keyboard Input Fields
        container.querySelectorAll(".pos-input").forEach(input => {
            // Highlight text on click/focus for fast typing
            input.onfocus = (e) => e.target.select();

            // Handle ENTER key or Arrow Up/Down keys
            input.onkeydown = (e) => {
                const slot = parseInt(e.target.dataset.slot, 10);
                let currentVal = parseInt(e.target.value, 10) || 0;

                if (e.key === "Enter") {
                    e.target.blur();
                } else if (e.key === "ArrowUp") {
                    e.preventDefault();
                    setRotorPosition(slot, currentVal + 1);
                } else if (e.key === "ArrowDown") {
                    e.preventDefault();
                    setRotorPosition(slot, currentVal - 1);
                }
            };

            // Update on blur (clicking away after typing number)
            input.onblur = (e) => {
                const slot = parseInt(e.target.dataset.slot, 10);
                setRotorPosition(slot, e.target.value);
            };
        });

        // Bind Step Buttons (Mouse Click Arrows)
        container.querySelectorAll(".step-btn").forEach(btn => {
            btn.onclick = (e) => {
                const slot = parseInt(e.target.dataset.slot, 10);
                const dir = e.target.dataset.dir;
                let currentPos = this.state.positions[slot];
                let newPos = dir === "up" ? currentPos + 1 : currentPos - 1;
                setRotorPosition(slot, newPos);
            };
        });
     }

    async processMessage() {
        const inputText = document.getElementById("input-text").value;
        if (!inputText) return;

        const data = await this.api("/api/process", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: inputText })
        });

        if (data) {
            if (data.output !== undefined) {
                document.getElementById("output-text").value = data.output;
            }
            if (data.state) {
                this.state = data.state;
                this.renderRotors();
            }
            // Pass the last character trace object to draw the SVG paths
            if (data.traces && data.traces.length > 0) {
                this.renderTraces(data.traces.at(-1));
            }
        }
    }

    renderTraces(trace) {
        const tracer = document.getElementById("tracerSvg");
        if (!tracer) return;

        // Display placeholder text if no trace data is available
        if (!trace) {
            tracer.innerHTML = `
                <text x="400" y="125" text-anchor="middle" fill="#4a596e" font-family="Courier New" font-size="14">
                    Process a message to render the electrical circuit signal path across 50 contacts
                </text>`;
            return;
        }

        // Map 50 contact positions (0 - 49) to Y coordinates inside SVG box
        const y = (contact) => 40 + (contact / 49) * 160;
        const start = 100;
        const step = 55;
        const reflector = 700;

        // 1. Draw background rectangles for 10 Rotors + 1 Reflector box
        let svg = Array.from({ length: 10 }, (_, slot) => {
            const x = start + (9 - slot) * step;
            return `<rect x="${x - 16}" y="30" width="32" height="180" fill="#18202a" stroke="#334357" rx="4"/>`;
        }).join('') + `<rect x="680" y="30" width="40" height="180" fill="#241b24" stroke="#ff3344" rx="4"/>`;

        const path = (points) => points.map(([x, vertical], i) => `${i ? 'L' : 'M'} ${x} ${vertical}`).join(' ');

        // 2. Map Green Forward Path (Right-to-Left through Rotors 10 down to 1 into Reflector)
        const forward = [
            [30, y(trace.inputIndex)],
            ...trace.forwardRotorPass.flatMap((item, i) => [
                [start + i * step - 10, y(item.contactIn)],
                [start + i * step + 10, y(item.contactOut)]
            ]),
            [reflector - 15, y(trace.reflectorEntryIndex)],
            [reflector + 15, y((trace.reflectorEntryIndex + trace.reflectorExitIndex) / 2)],
            [reflector - 15, y(trace.reflectorExitIndex)]
        ];

        // 3. Map Amber Dashed Return Path (Left-to-Right back through Rotors 1 up to 10)
        const backward = [
            [reflector - 15, y(trace.reflectorExitIndex)],
            ...trace.reverseRotorPass.flatMap((item, i) => [
                [start + (9 - i) * step + 10, y(item.contactIn)],
                [start + (9 - i) * step - 10, y(item.contactOut)]
            ]),
            [30, y(trace.outputIndex)]
        ];

        // 4. Inject SVG vector elements into the document DOM
        tracer.innerHTML = svg + `
            <path d="${path(forward)}" fill="none" stroke="#00e676" stroke-width="2.5"/>
            <path d="${path(backward)}" fill="none" stroke="#ffb300" stroke-width="2.5" stroke-dasharray="5,4"/>
        `;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    window.machine = new MachineController();
});