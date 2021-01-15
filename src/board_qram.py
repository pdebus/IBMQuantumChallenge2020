from qiskit import *
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import IBMQ, Aer, execute

import numpy as np
import matplotlib.pyplot as plt

from circuit_parts.diffusers import diffuser_gate
from utils.board_tools import find_closest_string, board2_bitstrings
from datasets.data import problem_set3x3, problem_set


def init_light_states(qc, lights, light_qubits):
    for i, light in enumerate(lights):
        if light == 0:
            qc.x(light_qubits[i])


def write_qram(boards, qc, address_qubits, data_qubits, ancilla_qubits=None):

    num_address_bits = len(address_qubits)
    closest_lights, _ = find_closest_string(boards)
    init_light_states(qc, closest_lights, data_qubits)

    num_ancillas = max(0, num_address_bits - 2)

    for n, board in enumerate(boards):
        for ab, bit in enumerate(format(n, f"0{num_address_bits}b")):
            if bit == '0':
                qc.x(address_qubits[ab])

        switches = np.equal(board, closest_lights)

        for db, switch in enumerate(switches):
            if not switch:
                if num_address_bits == 2:
                    qc.rccx(address_qubits[0], address_qubits[1], data_qubits[db])
                else:
                    if ancilla_qubits is not None and num_ancillas > 0:
                        qc.mct(address_qubits, data_qubits[db], ancilla_qubits[:num_ancillas], mode='basic')
                    else:
                        qc.mct(address_qubits, data_qubits[db])

        for ab, bit in enumerate(format(n, f"0{num_address_bits}b")):
            if bit == '0':
                qc.x(address_qubits[ab])


def qRAM(lights):

    address_size = int(np.log2(len(lights)))
    data_size = len(lights[0])

    address_qubits = QuantumRegister(address_size)
    data_qubits = QuantumRegister(data_size)
    qc = QuantumCircuit(address_qubits, data_qubits)

    closest_lights, _ = find_closest_string(lights)
    init_light_states(qc, closest_lights, data_qubits)

    for n, board in enumerate(lights):
        for ab, bit in enumerate(format(n, '02b')):
            if bit == '0':
                qc.x(address_qubits[ab])

        switches = np.equal(board, closest_lights)

        for db, switch in enumerate(switches):
            if not switch:
                qc.rccx(address_qubits[0], address_qubits[1], data_qubits[db])

        for ab, bit in enumerate(format(n, '02b')):
            if bit == '0':
                qc.x(address_qubits[ab])

    qram = qc.to_gate()
    qram.name = "$qRAM$"
    return qram


def test_qram_function(lights):
    print("\n===Write and measure Board QRAM (Function Version)===")

    num_address_bits = int(np.log2(len(lights)))
    num_lights = len(lights[0])

    # Create separate registers to name bits
    address_qubits = QuantumRegister(num_address_bits, name='address')
    light_qubits = QuantumRegister(num_lights, name='light')
    cbits = ClassicalRegister(num_lights + num_address_bits, name="cbits")
    qc = QuantumCircuit(address_qubits, light_qubits, cbits)

    # address preparation
    qc.h(address_qubits)
    qc.barrier()

    write_qram(lights, qc, address_qubits, light_qubits)

    # Check the qRAM　status
    qc.measure(address_qubits, cbits[0:num_address_bits])
    qc.measure(light_qubits, cbits[num_address_bits:])

    # Reverse the output string.
    qc = qc.reverse_bits()

    backend = Aer.get_backend('qasm_simulator')
    job = execute(qc, backend=backend, shots=8000, seed_simulator=12345)

    result = job.result()
    count = result.get_counts()
    for string, counts in dict(sorted(count.items())).items():
        print(f"Memory Cell: {string[:num_address_bits]} \tContent: {string[num_address_bits:]} \t Counts:{counts}")

    print("\nGroundtruth:")
    for light in lights:
        print("   " + "".join([f'{abs(c - 1)}' for c in light]))

    # qc.draw(output='mpl')
    # plt.show()


def test_qqram_gate(lights):
    print("\n===Write and measure Board QRAM (Gate Version)===")

    num_address_bits = int(np.log2(len(lights)))
    num_lights = len(lights[0])

    # Create separate registers to name bits
    address_qubits = QuantumRegister(num_address_bits, name='address')
    light_qubits = QuantumRegister(num_lights, name='light')
    cbits = ClassicalRegister(num_lights + num_address_bits, name="cbits")
    qc = QuantumCircuit(address_qubits, light_qubits, cbits)

    # address preparation
    qc.h(address_qubits)
    qc.barrier()

    qc.append(qRAM(lights), address_qubits[:] + light_qubits[:])

    # Check the qRAM　status
    qc.measure(address_qubits, cbits[0:num_address_bits])
    qc.measure(light_qubits, cbits[num_address_bits:])

    # Reverse the output string.
    qc = qc.reverse_bits()

    backend = Aer.get_backend('qasm_simulator')
    job = execute(qc, backend=backend, shots=8000, seed_simulator=12345)

    result = job.result()
    count = result.get_counts()
    for string, counts in dict(sorted(count.items())).items():
        print(f"Memory Cell: {string[:num_address_bits]} \tContent: {string[num_address_bits:]} \t Counts:{counts}")

    print("\nGroundtruth:")
    for light in lights:
        print("   " + "".join([f'{abs(c - 1)}' for c in light]))

    # qc.draw(output='mpl')
    # plt.show()


def test_board_qram_grover_read(lights):
    print("\n===Grover Read from Board QRAM===")
    print("Searching board with light 2 off in QRAM (Stored at 11)")

    num_address_bits = int(np.log2(len(lights)))
    num_lights = len(lights[0])

    # Create separate registers to name bits
    address_qubits = QuantumRegister(num_address_bits, name='address')
    light_qubits = QuantumRegister(num_lights, name='light')
    output_qubit = QuantumRegister(1, name='out')
    cbits = ClassicalRegister(num_lights + num_address_bits, name="cbits")

    qc = QuantumCircuit(light_qubits, address_qubits, output_qubit, cbits)

    # Initialization
    # Flag to |->
    qc.x(output_qubit)
    qc.h(output_qubit)

    # Address to |++>
    qc.h(address_qubits)
    qc.barrier()

    qc.append(qRAM(lights), address_qubits[:] + light_qubits[:])
    qc.cx(light_qubits[2], output_qubit)
    qc.append(qRAM(lights), address_qubits[:] + light_qubits[:])

    # Diffuser
    qc.append(diffuser_gate(num_address_bits), address_qubits)

    # Check the qRAM　status
    qc.measure(address_qubits, cbits[0:num_address_bits])
    qc.measure(light_qubits, cbits[num_address_bits:])

    # Reverse the output string.
    qc = qc.reverse_bits()

    # backend = provider.get_backend('ibmq_qasm_simulator')
    backend = Aer.get_backend('qasm_simulator')
    job = execute(qc, backend=backend, shots=1000)

    result = job.result()
    count = result.get_counts()
    for string, counts in dict(sorted(count.items())).items():
        print(f"Board number: {string[:num_address_bits]}\tCounts {counts}\tUncomputed QRAM: {string[num_address_bits:]}")

    # qc.draw(output='mpl')
    # plt.plot()


if __name__ == "__main__":

    # lightsout42 = [[1, 0, 1, 1],
    #                [0, 1, 1, 0],
    #                [1, 1, 1, 1],
    #                [0, 1, 0, 0]
    #                ]
    #
    # test_qram_function(lightsout42)
    # test_qqram_gate(lightsout42)
    # test_board_qram_grover_read(lightsout42)
    #
    # lightsout49 = [[1, 1, 1, 0, 0, 0, 1, 0, 0],
    #                [1, 0, 1, 0, 0, 0, 1, 1, 0],
    #                [1, 0, 1, 1, 1, 1, 0, 0, 1],
    #                [1, 0, 0, 0, 0, 0, 1, 0, 0]
    #                ]
    #
    # test_qram_function(lightsout49)
    # test_qqram_gate(lightsout49)
    # test_board_qram_grover_read(lightsout49)

    test_qram_function(board2_bitstrings(problem_set3x3, board_size=3))




