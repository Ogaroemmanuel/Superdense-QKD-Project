import streamlit as st
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram

# --- PAGE SETUP ---
st.set_page_config(page_title="Superdense QKD: 8-Bit Upgrade", layout="wide")
st.title("🔐 Multi-Bit Quantum Key Exchange")

# --- SIDEBAR: THE EVE LAB ---
st.sidebar.header("🦠 The 'Eve' Lab")
st.sidebar.markdown("Toggle this to simulate a man-in-the-middle attack.")
eve_active = st.sidebar.checkbox("Activate Eavesdropper (Eve)", value=False)

if eve_active:
    st.sidebar.error("🚨 WARNING: Eve is actively measuring the quantum channel!")
else:
    st.sidebar.success("✅ Channel is secure. No eavesdropping detected.")

# --- ALICE'S INPUT ---
st.write("#### 1. Alice Generates an 8-Bit Key")
# Default 8-bit string
message = st.text_input("Enter an 8-bit binary key (Must be exactly 8 characters):", "10110100")

if len(message) != 8 or not all(c in '01' for c in message):
    st.error("Please enter exactly 8 binary digits (0s and 1s).")
    st.stop()

# --- QUANTUM CIRCUIT (8 Qubits, 8 Classical Bits) ---
qc = QuantumCircuit(8, 8)

# Split the 8-bit message into 4 pairs: e.g., "10", "11", "01", "00"
pairs = [message[0:2], message[2:4], message[4:6], message[6:8]]

# Loop through each pair to Entangle, Encode, Attack, and Decode
for i, pair in enumerate(pairs):
    q_alice = 2 * i       # Even numbered qubits (0, 2, 4, 6)
    q_bob = 2 * i + 1     # Odd numbered qubits (1, 3, 5, 7)
    
    # 1. Entangle
    qc.h(q_alice)
    qc.cx(q_alice, q_bob)
    
    # 2. Encode
    if pair == "01": 
        qc.z(q_alice)
    elif pair == "10": 
        qc.x(q_alice)
    elif pair == "11": 
        qc.z(q_alice)
        qc.x(q_alice)
    
    # 3. Eve Attacks! (She intercepts Alice's qubits in transit)
    if eve_active:
        qc.measure(q_alice, q_alice)
        
    # 4. Decode
    qc.cx(q_alice, q_bob)
    qc.h(q_alice)

# 5. Final Measurement (Measure all 8 qubits into 8 classical bits)
qc.measure(range(8), range(8))

# --- SIMULATION ---
simulator = AerSimulator()
result = simulator.run(qc, shots=1000).result()
counts = result.get_counts()

# --- RESULTS & QBER ---
st.write("#### 2. Bob's Measurement Results")

# FIX: Qiskit outputs qubit strings from right-to-left. 
# We must reverse the order of our 4 pairs to match Qiskit's exact output.
qiskit_target_string = "".join(reversed(pairs))

total_shots = 1000
correct_shots = counts.get(qiskit_target_string, 0)
qber = ((total_shots - correct_shots) / total_shots) * 100

st.write("### Security Analysis")

# Display the QBER metric and Alert side-by-side
col1, col2 = st.columns([1, 2])
with col1:
    st.metric("Quantum Bit Error Rate (QBER)", f"{qber}%")
    
with col2:
    if qber > 11.0:
        st.error("🚨 CRITICAL ALERT: Eavesdropper detected! Key destroyed. Do not trust this connection.")
    else:
        st.success(f"✅ TRANSMISSION SUCCESSFUL: The 8-bit key (**{message}**) was received safely by Bob with no interruption.")

# --- PROFESSIONAL QISKIT GRAPH ---
st.write("#### Quantum Histogram")
if eve_active:
    st.write("Eve collapsed the wavefunction! The single correct key exploded into 256 random wrong combinations.")
    fig = plot_histogram(counts, color='crimson', figsize=(15, 5)) # Turns red when hacked
    ax = fig.gca()
    ax.axes.xaxis.set_ticklabels([]) # Hides the messy labels when hacked
else:
    st.write("Clean quantum channel. 100% of the photons delivered the correct sequence.")
    fig = plot_histogram(counts, color='midnightblue', figsize=(15, 5))
    
st.pyplot(fig)