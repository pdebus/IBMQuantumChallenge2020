from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import IBMQ, Aer, execute


def diffuser_old(nqubits):
    qc = QuantumCircuit(nqubits)
    # Apply transformation |s> -> |00..0> (H-gates)
    for qubit in range(nqubits):
        qc.h(qubit)
    # Apply transformation |00..0> -> |11..1> (X-gates)
    for qubit in range(nqubits):
        qc.x(qubit)
    # Do multi-controlled-Z gate
    qc.h(nqubits-1)
    qc.mct(list(range(nqubits-1)), nqubits-1)  # multi-controlled-toffoli
    qc.h(nqubits-1)
    # Apply transformation |11..1> -> |00..0>
    for qubit in range(nqubits):
        qc.x(qubit)
    # Apply transformation |00..0> -> |s>
    for qubit in range(nqubits):
        qc.h(qubit)
    # We will return the diffuser as a gate
    U_s = qc.to_gate()
    U_s.name = "$U_s$"
    return U_s


def diffuser(qc, diffusion_qubits, ancilla_qubits=None):

    if ancilla_qubits is not None:
        assert len(ancilla_qubits) >= len(diffusion_qubits) - 2

    # Apply transformation |s> -> |00..0> (H-gates)
    qc.h(diffusion_qubits)
    # Apply transformation |00..0> -> |11..1> (X-gates)
    qc.x(diffusion_qubits)

    # Do multi-controlled-Z gate
    qc.h(diffusion_qubits[-1])

    if ancilla_qubits is not None:
        qc.mct(diffusion_qubits[:-1], diffusion_qubits[-1], ancilla_qubits, mode='basic')
    else:
        qc.mct(diffusion_qubits[:-1], diffusion_qubits[-1])

    qc.h(diffusion_qubits[-1])

    # Apply transformation |11..1> -> |00..0>
    qc.x(diffusion_qubits)
    # Apply transformation |00..0> -> |s>
    qc.h(diffusion_qubits)
    # We will return the diffuser as a gate


def diffuser_gate(nqubits, use_ancillas=False):
    diffusion_qubits = QuantumRegister(nqubits, name='out')

    if use_ancillas:
        ancilla_qubits = QuantumRegister(nqubits - 2, name='ancilla')
        qc = QuantumCircuit(diffusion_qubits, ancilla_qubits)
    else:
        ancilla_qubits = None
        qc = QuantumCircuit(diffusion_qubits)

    diffuser(qc, diffusion_qubits, ancilla_qubits)

    U_s = qc.to_gate()
    U_s.name = "$U_s$"
    return U_s