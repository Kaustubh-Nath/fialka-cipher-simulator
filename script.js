class MachineController {

    constructor() {

        this.state = null;

        this.selectedConfiguration = null;

    }

    async api(url, options = {}) {

        const response = await fetch(url, options);

        return await response.json();

    }

    async loadState() {

        const data = await this.api("/api/state");

        this.state = data.state;

        this.render();

    }

    render() {

        console.log("Current Machine State:");

        console.table(this.state);

    }

}


const machine = new MachineController();

machine.loadState();

const inputBox = document.getElementById("input-text");
const outputBox = document.getElementById("output-text");

document.getElementById("copy-input").onclick = async () => {

    await navigator.clipboard.writeText(inputBox.value);

};

document.getElementById("copy-output").onclick = async () => {

    await navigator.clipboard.writeText(outputBox.value);

};

document.getElementById("clear-input").onclick = () => {

    inputBox.value = "";

};

document.getElementById("clear-output").onclick = () => {

    outputBox.value = "";

};