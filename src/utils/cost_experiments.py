from qiskit import *
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import IBMQ, Aer, execute

from utils.grader_utils import compute_cost


def mct_reference_6qubit():
    board_qubits = QuantumRegister(8, name='board')
    output_qubit = QuantumRegister(1, name='out')
    ancilla_qubits = QuantumRegister(7, name='ancilla')

    qc = QuantumCircuit(board_qubits, output_qubit, ancilla_qubits)
    qc.mct(board_qubits[:6], output_qubit, ancilla_qubits, mode='basic')
    qc.mct([*board_qubits[:4], board_qubits[6], board_qubits[7]], output_qubit, ancilla_qubits, mode='basic')

    return qc


def overlap4_check():
    board_qubits = QuantumRegister(8, name='board')
    output_qubit = QuantumRegister(1, name='out')
    ancilla_qubits = QuantumRegister(7, name='ancilla')

    qc = QuantumCircuit(board_qubits, output_qubit, ancilla_qubits)
    qc.rcccx(*board_qubits[:3], ancilla_qubits[0])
    qc.rcccx(*board_qubits[3:6], ancilla_qubits[1])
    qc.rcccx(board_qubits[3], board_qubits[6], board_qubits[7], ancilla_qubits[2])

    qc.rccx(ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3])
    qc.cx(ancilla_qubits[1], ancilla_qubits[3])
    qc.cx(ancilla_qubits[2],  ancilla_qubits[3])

    qc.ccx(ancilla_qubits[3], ancilla_qubits[0], output_qubit)

    return qc


def mct_reference_12qubit():
    board_qubits = QuantumRegister(12, name='board')
    output_qubit = QuantumRegister(1, name='out')
    ancilla_qubits = QuantumRegister(7, name='ancilla')

    qc = QuantumCircuit(board_qubits, output_qubit, ancilla_qubits)
    qc.mct(board_qubits[:6], output_qubit, ancilla_qubits, mode='basic')
    qc.mct([*board_qubits[:3], *board_qubits[6:9]], output_qubit, ancilla_qubits, mode='basic')
    qc.mct([*board_qubits[:3], *board_qubits[9:12]], output_qubit, ancilla_qubits, mode='basic')

    return qc


def overlap3_check():
    board_qubits = QuantumRegister(12, name='board')
    output_qubit = QuantumRegister(1, name='out')
    ancilla_qubits = QuantumRegister(7, name='ancilla')

    qc = QuantumCircuit(board_qubits, output_qubit, ancilla_qubits)
    qc.rcccx(*board_qubits[:3], ancilla_qubits[0])
    qc.rcccx(*board_qubits[3:6], ancilla_qubits[1])
    qc.rcccx(*board_qubits[6:9], ancilla_qubits[2])
    qc.rcccx(*board_qubits[9:12], ancilla_qubits[3])

    qc.rccx(ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[4])
    qc.cx(ancilla_qubits[1], ancilla_qubits[4])
    qc.cx(ancilla_qubits[2],  ancilla_qubits[4])

    qc.rccx(ancilla_qubits[2], ancilla_qubits[4], ancilla_qubits[5])
    qc.cx(ancilla_qubits[2], ancilla_qubits[5])
    qc.cx(ancilla_qubits[4], ancilla_qubits[5])

    qc.ccx(ancilla_qubits[5], ancilla_qubits[0], output_qubit)

    return qc


if __name__ == "__main__":
    ref = mct_reference_6qubit()
    overlap = overlap4_check()

    print(f"6 Qubit Reference: {compute_cost(ref)}")
    print(f"6 Qubit Overlap: {compute_cost(overlap)}")

    ref = mct_reference_12qubit()
    overlap = overlap3_check()

    print(f"12 Qubit Reference: {compute_cost(ref)}")
    print(f"12 Qubit Overlap: {compute_cost(overlap)}")
