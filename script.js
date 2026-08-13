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
            if (data.traces) {
                this.renderTraces(data.traces);
            }
        }
    }

    renderTraces(traces) {
        const traceBox = document.getElementById("trace-container");
        if (!traceBox) return;

        traceBox.innerHTML = "";

        const validTraces = traces.filter(t => t !== null && t !== undefined);
        if (validTraces.length === 0) {
            traceBox.innerHTML = "<p class='no-trace'>No signal traces generated.</p>";
            return;
        }

        validTraces.forEach((trace, idx) => {
            const traceItem = document.createElement("div");
            traceItem.className = "trace-block";

            // Format forward rotor pass
            const fwdPassStr = trace.forwardRotorPass ? 
                trace.forwardRotorPass.map(s => `Slot${s.slot + 1}:${s.contactIn}→${s.wireOut}`).join(" | ") : "";

            // Format reverse rotor pass
            const revPassStr = trace.reverseRotorPass ? 
                trace.reverseRotorPass.map(s => `Slot${s.slot + 1}:${s.contactIn}→${s.wireOut}`).join(" | ") : "";

            traceItem.innerHTML = `
                <div class="trace-char-header">Char #${idx + 1}: <strong>'${trace.inputChar}' ➔ '${trace.outputChar}'</strong></div>
                <div class="trace-line trace-fwd"><span class="pass-tag">[FWD]:</span> ${fwdPassStr}</div>
                <div class="trace-line trace-refl"><span class="pass-tag">[REFL]:</span> Bounce Contact ${trace.reflectorEntryIndex} ➔ ${trace.reflectorExitIndex}</div>
                <div class="trace-line trace-rev"><span class="pass-tag">[REV]:</span> ${revPassStr}</div>
            `;
            
            traceBox.appendChild(traceItem);
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    window.machine = new MachineController();
});