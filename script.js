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
                    <span class="pos-num">${String(currentPosNum).padStart(2, '0')}</span>
                    <span class="pos-char">${currentPosChar}</span>
                </div>
                <button class="step-btn" data-slot="${slot}" data-dir="down">▼</button>
            `;

            container.appendChild(card);
        }

        // Bind rotor selection dropdowns
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

        // Bind step buttons
        container.querySelectorAll(".step-btn").forEach(btn => {
            btn.onclick = async (e) => {
                const slot = parseInt(e.target.dataset.slot, 10);
                const dir = e.target.dataset.dir;
                let currentPos = this.state.positions[slot];
                let newPos = dir === "up" ? (currentPos + 1) % 50 : (currentPos - 1 + 50) % 50;

                const data = await this.api("/api/configure", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ slot, position: newPos })
                });
                if (data.state) {
                    this.state = data.state;
                    this.renderRotors();
                }
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

        const validTraces = traces.filter(t => t !== null);
        if (validTraces.length === 0) {
            traceBox.innerHTML = "<p class='no-trace'>No signal traces generated.</p>";
            return;
        }

        validTraces.forEach((trace, idx) => {
            const traceItem = document.createElement("div");
            traceItem.className = "trace-item";

            const fwdPassStr = trace.forwardRotorPass ? trace.forwardRotorPass.map(s => `Slot${s.slot + 1}:${s.contactIn}→${s.wireOut}`).join(" | ") : "";
            const revPassStr = trace.reverseRotorPass ? trace.reverseRotorPass.map(s => `Slot${s.slot + 1}:${s.contactIn}→${s.wireOut}`).join(" | ") : "";

            traceItem.innerHTML = `
                <div class="trace-header">Char #${idx + 1}: <strong>'${trace.inputChar}'</strong> ➔ <strong>'${trace.outputChar}'</strong></div>
                <div class="trace-details">
                    <span class="trace-fwd">[FWD]: ${fwdPassStr}</span><br/>
                    <span class="trace-refl">[REFL]: Bounce Contact ${trace.reflectorEntryIndex} ➔ ${trace.reflectorExitIndex}</span><br/>
                    <span class="trace-rev">[REV]: ${revPassStr}</span>
                </div>
            `;
            traceBox.appendChild(traceItem);
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    window.machine = new MachineController();
});