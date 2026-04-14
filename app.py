# -*- coding: utf-8 -*-

import streamlit as st
import os

st.set_page_config(page_title="FRIDAY AI", layout="wide")

# -----------------------------
# HEADER
# -----------------------------
st.title("🧠 F.R.I.D.A.Y Control Panel")
st.caption("Fully Responsive Intelligent Digital Assistant for You")

# -----------------------------
# STATUS PANEL
# -----------------------------
st.subheader("System Status")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Core", "Online")

with col2:
    st.metric("Voice Engine", "Idle")

with col3:
    st.metric("Wake System", "Listening")

# -----------------------------
# CONTROL PANEL
# -----------------------------
st.subheader("Controls")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶ Start FRIDAY"):
        st.success("FRIDAY Core Starting...")
        os.system("echo Starting Friday")  # placeholder

with col2:
    if st.button("⏹ Stop FRIDAY"):
        st.warning("FRIDAY Core Stopping...")
        os.system("echo Stopping Friday")

with col3:
    if st.button("🔁 Restart"):
        st.info("Restarting system...")
        os.system("echo Restarting")

# -----------------------------
# COMMAND TERMINAL
# -----------------------------
st.subheader("Command Terminal")

command = st.text_input("Enter command")

if st.button("Execute"):
    if command:
        st.write(f"Executing: {command}")
        os.system(command)

# -----------------------------
# LOG PANEL
# -----------------------------
st.subheader("System Logs")

st.code("FRIDAY initialized...\nWaiting for commands...")