from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import IBMQ, Aer, execute

import matplotlib.pyplot as plt

def replace_op_half_adder():
    q = QuantumRegister(2, name='operands')
    res = QuantumRegister(1, name='results')
    qc = QuantumCircuit(q, res)

    # CarryOut
    qc.ccx(q[0], q[1], res[0])

    # SUM
    qc.cx(q[0], q[1])

    gate = qc.to_gate()
    gate.name = "HAro"

    return gate


def half_adder():
    q = QuantumRegister(2, name='operands')
    res = QuantumRegister(2, name='results')
    qc = QuantumCircuit(q, res)

    # SUM
    qc.cx(q[0], res[1])
    qc.cx(q[1], res[1])

    # CarryOut
    qc.ccx(q[0], q[1], res[0])

    gate = qc.to_gate()
    gate.name = "HA"

    return gate


def full_adder():
    q = QuantumRegister(3, name='operands')
    res = QuantumRegister(2, name='results')
    qc = QuantumCircuit(q, res)

    # SUM
    qc.cx(q[0], res[1])
    qc.cx(q[1], res[1])
    qc.cx(q[2], res[1])

    # CarryOut
    qc.ccx(q[0], q[1], res[0])
    qc.ccx(q[0], q[2], res[0])
    qc.ccx(q[1], q[2], res[0])

    gate = qc.to_gate()
    gate.name = "FA"

    return gate


def replace_carry_full_adder():
    q = QuantumRegister(4, name='operands')
    qc = QuantumCircuit(q)

    qc.ccx(q[0], q[1], q[3])
    qc.cx(q[0], q[1])
    qc.ccx(q[1], q[2], q[3])
    qc.cx(q[1], q[2])
    qc.cx(q[0], q[1])

    gate = qc.to_gate()
    gate.name = "FArc"

    return gate


def counter_4bit_gate():
    op_qubits = QuantumRegister(4, name='operands')
    ancilla_qubits = QuantumRegister(3, name='ancilla')

    qc = QuantumCircuit(op_qubits, ancilla_qubits)

    qc.append(replace_carry_full_adder(), op_qubits[:3] + [ancilla_qubits[0]])
    qc.append(replace_op_half_adder(), [op_qubits[2], op_qubits[3], ancilla_qubits[1]])
    qc.append(replace_op_half_adder(), [ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]])

    qc.swap(op_qubits[3], ancilla_qubits[0])

    counter = qc.to_gate()
    counter.name = "Counter"

    return counter


def counter_4bit(draw=False):
    op_qubits = QuantumRegister(4, name='operands')
    ancilla_qubits = QuantumRegister(3, name='ancilla')
    cbits = ClassicalRegister(3, name='cbits')

    qc = QuantumCircuit(op_qubits, ancilla_qubits, cbits)

    qc.x(op_qubits[0])
    qc.x(op_qubits[1])
    qc.x(op_qubits[2])
    qc.x(op_qubits[3])

    qc.append(counter_4bit_gate(), op_qubits[:] + ancilla_qubits[:])
    # qc.append(replace_carry_full_adder(), op_qubits[:3] + [ancilla_qubits[0]])
    # qc.append(replace_op_half_adder(), [op_qubits[2], op_qubits[3], ancilla_qubits[1]])
    # qc.append(replace_op_half_adder(), [ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]])
    #
    # qc.swap(op_qubits[3], ancilla_qubits[0])

    qc.measure(ancilla_qubits, cbits)
    # qc.measure(ancilla_qubits[0], cbits[0])
    # qc.measure(ancilla_qubits[1], cbits[1])
    # qc.measure(ancilla_qubits[2], cbits[2])

    if draw:
        qc.draw(output='mpl')
        plt.show()

    backend = Aer.get_backend('qasm_simulator')
    job = execute(qc, backend, shots=1000)
    result = job.result()
    count = result.get_counts()

    max_k = min(len(count), 10)

    for k in sorted(count, key=count.get, reverse=True)[:max_k]:
        print(f"Solution: {k}\tCounts: {count[k]}")


def counter_9bit_gate():
    op_qubits = QuantumRegister(9, name='operands')
    ancilla_qubits = QuantumRegister(7, name='ancilla')

    qc = QuantumCircuit(op_qubits, ancilla_qubits)

    qc.append(replace_carry_full_adder(), op_qubits[:3] + [ancilla_qubits[0]])
    qc.append(replace_carry_full_adder(), op_qubits[3:6] + [ancilla_qubits[1]])
    qc.append(replace_carry_full_adder(), op_qubits[6:] + [ancilla_qubits[2]])

    qc.append(replace_carry_full_adder(), ancilla_qubits[:3] + [ancilla_qubits[3]])
    qc.append(replace_carry_full_adder(), [op_qubits[2], op_qubits[5], op_qubits[8], ancilla_qubits[4]])

    qc.append(replace_op_half_adder(), [ancilla_qubits[2], ancilla_qubits[4], ancilla_qubits[5]])
    qc.append(replace_op_half_adder(), [ancilla_qubits[3], ancilla_qubits[5], ancilla_qubits[6]])

    qc.swap(ancilla_qubits[3], op_qubits[8])

    counter = qc.to_gate()
    counter.name = "Counter"

    return counter


def counter_9bit(draw=False):
    op_qubits = QuantumRegister(9, name='operands')
    ancilla_qubits = QuantumRegister(7, name='ancilla')
    cbits = ClassicalRegister(4, name='cbits')

    qc = QuantumCircuit(op_qubits, ancilla_qubits, cbits)

    # qc.x(op_qubits[0])
    # qc.x(op_qubits[1])
    # qc.x(op_qubits[2])
    qc.x(op_qubits[3])
    qc.x(op_qubits[4])
    qc.x(op_qubits[5])
    qc.x(op_qubits[6])
    qc.x(op_qubits[7])
    qc.x(op_qubits[8])

    qc.append(counter_9bit_gate(), op_qubits[:] + ancilla_qubits[:])
    qc.measure(ancilla_qubits[3:], cbits)

    if draw:
        qc.draw(output='mpl')
        plt.show()

    backend = Aer.get_backend('qasm_simulator')
    job = execute(qc, backend, shots=1000)
    result = job.result()
    count = result.get_counts()

    max_k = min(len(count), 10)

    for k in sorted(count, key=count.get, reverse=True)[:max_k]:
        print(f"Solution: {k}\tCounts: {count[k]}")


if __name__ == "__main__":
    #counter_4bit()
    counter_9bit()
