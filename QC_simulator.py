import math
import time
import sys

# ==========================================
# 1. STATE INITIALIZATION & BASE GATES
# ==========================================

def initialize_state(num_qubits, target_basis=0):
    """
    Creates a state vector for n qubits.
    target_basis: an integer representing the binary state to initialize.
                  (e.g., for 2 qubits, target_basis=3 initializes |11>)
    """
    dimension = 2 ** num_qubits 
    
    if target_basis < 0 or target_basis >= dimension:
        raise ValueError(f"Target basis {target_basis} is out of bounds for {num_qubits} qubits.")
        
    state_vector = [0.0 + 0.0j] * dimension
    
    # Set the specific requested basis state to 100% probability
    state_vector[target_basis] = 1.0 + 0.0j
    
    return state_vector

# 2x2 Single-Qubit Gates
X_GATE = [
    [0.0 + 0.0j, 1.0 + 0.0j],
    [1.0 + 0.0j, 0.0 + 0.0j]
]

h_val = 1.0 / math.sqrt(2)
H_GATE = [
    [h_val + 0.0j,  h_val + 0.0j],
    [h_val + 0.0j, -h_val + 0.0j]
]

I_GATE = [
    [1.0 + 0.0j, 0.0 + 0.0j],
    [0.0 + 0.0j, 1.0 + 0.0j]
]

# 4x4 Two-Qubit Controlled-NOT Gate (Control=Qubit 0, Target=Qubit 1)
CNOT_GATE = [
    [1.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
    [0.0 + 0.0j, 1.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
    [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 1.0 + 0.0j],
    [0.0 + 0.0j, 0.0 + 0.0j, 1.0 + 0.0j, 0.0 + 0.0j]
]

# ==========================================
# 2. CORE LINEAR ALGEBRA ENGINE
# ==========================================

def native_kron(A, B):
    """Computes the Kronecker product of two 2D matrices."""
    row_A, col_A = len(A), len(A[0])
    row_B, col_B = len(B), len(B[0])
    
    new_rows = row_A * row_B
    new_cols = col_A * col_B
    result = [[0.0 + 0.0j] * new_cols for _ in range(new_rows)]
    
    for i in range(row_A):
        for j in range(col_A):
            for k in range(row_B):
                for l in range(col_B):
                    target_row = i * row_B + k
                    target_col = j * col_B + l
                    result[target_row][target_col] = A[i][j] * B[k][l]
                    
    return result

def native_matrix_vector_multiply(matrix, vector):
    """Multiplies a 2D matrix by a 1D vector to transform the state."""
    size = len(vector)
    new_vector = [0.0 + 0.0j] * size
    
    for i in range(size):          
        for j in range(size):     
            new_vector[i] += matrix[i][j] * vector[j]
            
    return new_vector

# ==========================================
# 3. MULTI-QUBIT GATE ROUTING
# ==========================================

def apply_single_qubit_gate(state_vector, gate, target_qubit, num_qubits):
    """Expands a 1-qubit gate across the full system and applies it."""
    if target_qubit == 0:
        full_matrix = gate
    else:
        full_matrix = I_GATE

    for i in range(1, num_qubits):
        if i == target_qubit:
            full_matrix = native_kron(full_matrix, gate)
        else:
            full_matrix = native_kron(full_matrix, I_GATE)
            
    return native_matrix_vector_multiply(full_matrix, state_vector)

def apply_cnot_01(state_vector, num_qubits):
    """Applies a CNOT gate with Control=Qubit 0 and Target=Qubit 1, padding trailing qubits."""
    if num_qubits < 2:
        raise ValueError("The Bell State / CNOT workflow requires at least 2 qubits.")
        
    full_matrix = CNOT_GATE
    # Dynamically pad idle qubits using Kronecker products with the Identity matrix
    for _ in range(2, num_qubits):
        full_matrix = native_kron(full_matrix, I_GATE)
        
    return native_matrix_vector_multiply(full_matrix, state_vector)

# ==========================================
# 4. MEASUREMENT & PROBABILITIES
# ==========================================

def display_probabilities(state_vector, num_qubits):
    """Calculates and displays measurement probabilities for all states."""
    print("\n--- Measurement Probabilities ---")
    total_prob = 0.0
    
    for i in range(len(state_vector)):
        # Calculate P = |a + bj|^2 = a^2 + b^2
        prob = abs(state_vector[i]) ** 2
        total_prob += prob
        
        # Convert index into binary representation
        state_binary = format(i, f'0{num_qubits}b')
        print(f"State |{state_binary}>: Probability = {prob:.4f} (Amplitude: {state_vector[i]})")
        
    print(f"Total Probability Sum: {total_prob:.4f}")

# ==========================================
# 5. CIRCUIT EXECUTION & KPI TRACKING
# ==========================================

if __name__ == "__main__":
    print("=== Phoenix Quantum Simulator ===")
    
    # 1. Interactive & Validated User Input
    while True:
        try:
            num_qubits = int(input("Enter number of qubits (2 to 4): "))
            if 2 <= num_qubits <= 4:
                break
            else:
                print("Warning: Please select between 2 and 4 qubits to execute the Bell State / GHZ workflow.")
        except ValueError:
            print("Invalid input. Please enter a whole number.")

    dimension = 2 ** num_qubits
    
    # 2. Arbitrary Basis Initialization
    while True:
        try:
            basis_input = int(input(f"Enter initial target state as an integer (0 to {dimension - 1}): "))
            if 0 <= basis_input < dimension:
                break
            else:
                print(f"Out of bounds! For {num_qubits} qubits, states range from 0 to {dimension - 1}.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    print("\nInitializing Circuit Execution Pipeline...")
    
    # Track metrics from the very beginning of structural compilation
    start_total_time = time.perf_counter()
    state = initialize_state(num_qubits, target_basis=basis_input)
    
    # Show the initial bitstring configuration
    binary_format = format(basis_input, f'0{num_qubits}b')
    print(f"System successfully initialized in state: |{binary_format}>")
    
    # Calculate state vector memory size (approximation based on list element size)
    estimated_memory = sys.getsizeof(state) + sum(sys.getsizeof(element) for element in state)
    print(f"Initial State Vector Size: {len(state)} elements")
    print(f"Estimated Vector Memory Usage: {estimated_memory} bytes")
    
    print("\nExecuting Gates...")
    
    # Step 1: Apply H Gate to Qubit 0
    start_gate = time.perf_counter()
    state = apply_single_qubit_gate(state, H_GATE, target_qubit=0, num_qubits=num_qubits)
    h_gate_time = time.perf_counter() - start_gate
    print(f"-> H Gate Execution Time: {h_gate_time:.6f} seconds")
    
    # Step 2: Apply CNOT Gate (Control=0, Target=1)
    start_gate = time.perf_counter()
    state = apply_cnot_01(state, num_qubits=num_qubits)
    cnot_gate_time = time.perf_counter() - start_gate
    print(f"-> CNOT Gate Execution Time: {cnot_gate_time:.6f} seconds")
    
    # Calculate total running time
    total_execution_time = time.perf_counter() - start_total_time
    print(f"\nTotal Pipeline Execution Time: {total_execution_time:.6f} seconds")
    
    # Display Final Results
    display_probabilities(state, num_qubits)
    