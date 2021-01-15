from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import IBMQ, Aer, execute

import matplotlib.pyplot as plt


def five_qubit_custom_sp(draw=False):
    qubits = QuantumRegister(5, name='qubits')
    cbits = ClassicalRegister(5, name='cbits')

    qc = QuantumCircuit(qubits, cbits)

    qc.h(qubits[0])
    qc.h(qubits[3:])

    qc.measure(qubits, cbits)

    if draw:
        qc.draw(output='mpl')
        plt.show()

    backend = Aer.get_backend('qasm_simulator')
    job = execute(qc, backend, shots=1000)
    result = job.result()
    count = result.get_counts()
    print(count)


if __name__ == "__main__":
    five_qubit_custom_sp()
