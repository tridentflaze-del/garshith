INSTRUCTIONS TO RUN THE QC SIMULATOR: 

    ---> Run the script in your terminal or VS Code environment ( QC_simulator.py)

    --->Enter Qubit size of the system: When the prompt asks Enter number of qubits (1 to 4) ( type 2 so that the bell state workflow can run )

    ---> Enter Initial State: When it asks for the initial target state ( type 0 and hit Enter. This ensures your system starts cleanly at ∣00⟩ which is the standard initial state for BSW )

    ---> OUTPUT:
                The program will print out the sizes, times, and final probabilities on the terminal.



MEMORY AND TIME-SCALING ANALYSIS:

     ---> The Memory Bottleneck:
                 In this native Python simulator, memory scales exponentially with the number of qubits (n). The state vector requires an array of size 2n. For a small system like 3 qubits, this is only 8 complex numbers. However, at 20                 qubits, the array requires 1,048,576 elements. At 30 qubits, it demands over a billion elements. Because Python stores each complex number with significant byte overhead, a 30-qubit simulation would require gigabytes of raw RAM just to store the initial state, inevitably leading to a memory exhaustion crash (Out of Memory error) on standard hardware.


    --->The Execution Time Bottleneck:
                  The execution time is heavily penalized by the nested loops in our native_matrix_vector_multiply and native_kron functions. Matrix multiplication time complexity for an N×N matrix is fundamentally O(N2) in our implementation. Since our matrix dimension is N=2n, the time complexity to apply a single expanded gate is O(22n). Adding just one more qubit to the system quadruples the size of the expanded matrix, causing the execution time to skyrocket rapidly.


HARDWARE ACCELERATION AND FPGA INTEGRATION:

      --->Why Python is Slow:
                   Our simulator computes sequentially. Python evaluates one loop iteration at a time, meaning calculating millions of matrix elements happens sequentially on a single CPU core.

          The Hardware Solution:
                    Real-world quantum simulators bypass software loops by using highly parallel hardware like GPUs or FPGAs (Field Programmable Gate Arrays).

              GPUs: Graphics processing units possess thousands of smaller cores designed specifically for parallel matrix multiplication. A GPU can compute entire rows of our 2n×2n matrix simultaneously.

              FPGAs: An FPGA allows engineers to physically wire the logic of the Kronecker product and matrix multiplication directly into silicon. Instead of fetching instructions from memory like a CPU, an FPGA streams the state vector   through physical hardware logic gates, executing the complex arithmetic with near-zero latency and massive parallelism.