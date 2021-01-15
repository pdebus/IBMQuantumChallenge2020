from qiskit import *
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import IBMQ, Aer, execute

import numpy as np
import matplotlib.pyplot as plt

from board_qram import write_qram, qRAM
from board_oracles import lights_out_oracle, lights_out_oracle_gate
from circuit_parts.diffusers import diffuser, diffuser_gate
from circuit_parts.adder import counter_4bit_gate, counter_9bit_gate


def simplified(lights, num_iterations=3):
    switch_qubits = QuantumRegister(9, name='switch')
    light_qubits = QuantumRegister(9, name='light')
    address_qubits = QuantumRegister(2, name='address')
    ancilla_qubits = QuantumRegister(7, name='ancilla')
    output_qubit = QuantumRegister(1, name='out')
    cbits = ClassicalRegister(2, name="cbits")
    qc = QuantumCircuit(switch_qubits, light_qubits, address_qubits, ancilla_qubits, output_qubit, cbits)

    # Initialization
    # Flag to |->
    qc.x(output_qubit)
    qc.h(output_qubit)

    # Address to |++>
    qc.h([address_qubits[0], address_qubits[1]])

    # Switch to |+++++++++>
    qc.h(switch_qubits)
    qc.barrier()

    write_qram(lights, qc, address_qubits, light_qubits)
    qc.barrier()
    for i in range(num_iterations):
        lights_out_oracle(qc, switch_qubits, light_qubits, output_qubit, ancilla_qubits)
        diffuser(qc, switch_qubits, ancilla_qubits)
    qc.barrier()

    qc.ccx(switch_qubits[2], switch_qubits[3], output_qubit)

    for i in range(num_iterations):
        lights_out_oracle(qc, switch_qubits, light_qubits, output_qubit, ancilla_qubits)
        diffuser(qc, switch_qubits, ancilla_qubits)
    qc.barrier()

    write_qram(lights, qc, address_qubits, light_qubits)
    diffuser(qc, address_qubits)

    qc.barrier()
    qc.measure(address_qubits, cbits)

    return qc


def downsized_problem(lights, num_iterations=3):
    switch_qubits = QuantumRegister(4, name='switch')
    light_qubits = QuantumRegister(4, name='light')
    address_qubits = QuantumRegister(2, name='address')
    ancilla_qubits = QuantumRegister(3, name='ancilla')
    output_qubit = QuantumRegister(1, name='out')
    cbits = ClassicalRegister(2, name="cbits")
    qc = QuantumCircuit(switch_qubits, light_qubits, address_qubits, ancilla_qubits, output_qubit, cbits)

    # Initialization
    # Flag to |->
    qc.x(output_qubit)
    qc.h(output_qubit)

    # Address to |++>
    qc.h(address_qubits)

    # Switch to |+++++++++>
    qc.h(switch_qubits)
    qc.barrier()

    write_qram(lights, qc, address_qubits, light_qubits)
    qc.barrier()

    for i in range(num_iterations):
        lights_out_oracle(qc, switch_qubits, light_qubits, output_qubit, ancilla_qubits)
        diffuser(qc, switch_qubits, ancilla_qubits)
    qc.barrier()

    # Simple oracle: selects solution [1,1,0,1] belonging to board [0,1,0,0] at location 11
    # qc.x(switch_qubits[2])
    # qc.ccx(switch_qubits[0], switch_qubits[2], output_qubit)
    # qc.x(switch_qubits[2])

    # Counter
    qc.append(counter_4bit_gate(), switch_qubits[:] + ancilla_qubits[:])

    # Select Solutions with only one switch, 2 MSB set to 0
    qc.x(ancilla_qubits[1:])
    # qc.x(ancilla_qubits[0])
    # qc.x(ancilla_qubits[2])
    qc.ccx(ancilla_qubits[0], ancilla_qubits[1], output_qubit)
    # qc.ccx(ancilla_qubits[0], ancilla_qubits[1], output_qubit)
    # qc.x(ancilla_qubits[2])
    # qc.x(ancilla_qubits[0])
    qc.x(ancilla_qubits[1:])

    qc.append(counter_4bit_gate().inverse(), switch_qubits[:] + ancilla_qubits[:])

    for i in range(num_iterations):
        lights_out_oracle(qc, switch_qubits, light_qubits, output_qubit, ancilla_qubits)
        diffuser(qc, switch_qubits, ancilla_qubits)
    qc.barrier()

    write_qram(lights, qc, address_qubits, light_qubits)
    diffuser(qc, address_qubits)

    qc.barrier()
    qc.measure(address_qubits, cbits)

    qc = qc.reverse_bits()

    return qc


def week2b_ans_func(lights, num_iterations=17):
    switch_qubits = QuantumRegister(9, name='switch')
    light_qubits = QuantumRegister(9, name='light')
    address_qubits = QuantumRegister(2, name='address')
    ancilla_qubits = QuantumRegister(7, name='ancilla')
    output_qubit = QuantumRegister(1, name='out')
    cbits = ClassicalRegister(2, name="cbits")
    qc = QuantumCircuit(switch_qubits, light_qubits, address_qubits, ancilla_qubits, output_qubit, cbits)

    # Initialization
    # Flag to |->
    qc.x(output_qubit)
    qc.h(output_qubit)

    # Address to |++>
    qc.h(address_qubits)

    # Switch to |+++++++++>
    qc.h(switch_qubits)
    qc.barrier()

    write_qram(lights, qc, address_qubits, light_qubits)
    qc.barrier()

    for i in range(num_iterations):
        lights_out_oracle(qc, switch_qubits, light_qubits, output_qubit, ancilla_qubits)
        diffuser(qc, switch_qubits, ancilla_qubits)
    qc.barrier()

    # Counter
    qc.append(counter_9bit_gate(), switch_qubits[:] + ancilla_qubits[:])

    # Select Solutions with only one switch, 2 MSB set to 0
    qc.x(ancilla_qubits[5:])
    qc.ccx(ancilla_qubits[5], ancilla_qubits[6], output_qubit)
    qc.x(ancilla_qubits[5:])

    qc.append(counter_9bit_gate().inverse(), switch_qubits[:] + ancilla_qubits[:])

    for i in range(num_iterations):
        lights_out_oracle(qc, switch_qubits, light_qubits, output_qubit, ancilla_qubits)
        diffuser(qc, switch_qubits, ancilla_qubits)
    qc.barrier()

    write_qram(lights, qc, address_qubits, light_qubits)
    diffuser(qc, address_qubits)

    qc.barrier()
    qc.measure(address_qubits, cbits)

    qc = qc.reverse_bits()

    return qc


def run_circuit(lights, qc_generator, draw=False):
    qc = qc_generator(lights)

    if draw:
        qc.draw(output='mpl')
        plt.show()

    backend = Aer.get_backend('qasm_simulator')
    job = execute(qc, backend, shots=1000)
    result = job.result()
    count = result.get_counts()

    for k in sorted(count, key=count.get, reverse=True):
        print(f"Solution: {k}\tCounts: {count[k]}")


if __name__ == "__main__":

    lightsout4 = [[1, 1, 1, 0, 0, 0, 1, 0, 0],
                  [1, 0, 1, 0, 0, 0, 1, 1, 0],
                  [1, 0, 1, 1, 1, 1, 0, 0, 1],
                  [1, 0, 0, 0, 0, 0, 1, 0, 0]
                  ]

    lightsout42 = [[1, 0, 1, 1],
                   [0, 1, 1, 0],
                   [1, 1, 1, 1],
                   [0, 1, 0, 0]
                   ]

    #run_circuit(lightsout42, lambda l: downsized_problem(l, num_iterations=3))
    run_circuit(lightsout4, week2b_ans_func)
