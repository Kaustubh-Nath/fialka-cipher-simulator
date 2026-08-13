import streamlit as st
from engine import FialkaEngine
from config import PRESETS
from configuration_manager import ConfigurationManager

st.set_page_config(page_title="Fialka M-125 Simulator", layout="wide")

# Initialize persistent session state engine
if "engine" not in st.session_state:
    st.session_state.engine = FialkaEngine()

engine = st.session_state.engine

st.title("FIALKA M-125 SIMULATOR")

# Layout: Left Panel (Config) & Right Panel (Console)
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Machine Configuration")
    
    # Rotor Positions Reset / Presets
    if st.button("Reset Rotor Positions"):
        engine.reset_positions()
        st.success("Rotor positions reset to zero!")

    preset_choice = st.selectbox("Load Key Preset", ["-- Select Preset --"] + list(PRESETS.keys()))
    if preset_choice != "-- Select Preset --":
        if st.button("Apply Preset"):
            engine.rotors.rotor_order = list(PRESETS[preset_choice]["rotor_order"])
            engine.rotors.positions = list(PRESETS[preset_choice]["positions"])
            st.success(f"Applied preset '{preset_choice}'!")

    st.markdown("---")
    st.subheader("Saved Configurations")
    config_name = st.text_input("Configuration Name")
    if st.button("Save Configuration"):
        if config_name.strip():
            ConfigurationManager.save(engine, config_name.strip())
            st.success(f"Saved configuration '{config_name.strip()}'")

    saved_configs = ConfigurationManager.list()
    if saved_configs:
        selected_config = st.selectbox("Saved Sets", saved_configs)
        if st.button("Load Configuration"):
            ConfigurationManager.load(engine, selected_config)
            st.success(f"Loaded '{selected_config}'")

with col2:
    st.subheader("Encryption Console")

    input_text = st.text_area("Input Text:", value="", height=150)
    
    if st.button("Process Message", type="primary"):
        if input_text:
            output_text, traces = engine.process_text(input_text)
            st.session_state["output_text"] = output_text
            st.session_state["traces"] = traces
        else:
            st.warning("Please enter text to encipher/decipher.")

    output_val = st.session_state.get("output_text", "")
    st.text_area("Output Result:", value=output_val, height=150, disabled=True)

    # Signal Trace View
    if "traces" in st.session_state and st.session_state["traces"]:
        with st.expander("Show Signal Trace Log"):
            st.json(st.session_state["traces"])