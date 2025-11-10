# Step 4: Quantum Circuit Design for Protein Structure Prediction

from qiskit import QuantumCircuit
from qiskit.circuit import Parameter, ParameterVector
from qiskit.circuit.library import EfficientSU2, TwoLocal, RealAmplitudes
import numpy as np
import matplotlib.pyplot as plt

class ProteinQuantumCircuit:
    """
    Designs and builds the parameterized quantum circuit (ansatz) 
    for protein structure prediction using VQE.
    """
    
    def __init__(self, num_qubits, hamiltonian_info):
        self.num_qubits = num_qubits
        self.hamiltonian_info = hamiltonian_info
        self.circuit = None
        self.parameters = None
        
    def create_initial_state(self):
        """
        Creates the initial quantum state with Hadamard gates.
        Puts all qubits in superposition to explore all possible conformations.
        """
        init_circuit = QuantumCircuit(self.num_qubits)
        
        # Apply Hadamard to all qubits for equal superposition
        for qubit in range(self.num_qubits):
            init_circuit.h(qubit)
        
        print(f"✓ Initial state: All {self.num_qubits} qubits in superposition")
        return init_circuit
    
    def create_efficient_su2_ansatz(self, reps=3):
        """
        Creates an EfficientSU2 ansatz - a hardware-efficient circuit.
        Good balance between expressibility and circuit depth.
        
        Args:
            reps: Number of repetitions (circuit depth)
        """
        ansatz = EfficientSU2(
            num_qubits=self.num_qubits,
            reps=reps,
            entanglement='linear',  # Linear connectivity
            insert_barriers=True
        )
        
        num_params = ansatz.num_parameters
        print(f"✓ EfficientSU2 ansatz created:")
        print(f"  - Repetitions: {reps}")
        print(f"  - Total parameters: {num_params}")
        print(f"  - Circuit depth: ~{ansatz.depth()}")
        
        return ansatz
    
    def create_twolocal_ansatz(self, reps=3):
        """
        Creates a TwoLocal ansatz with customizable gates.
        More flexible than EfficientSU2.
        
        Args:
            reps: Number of repetitions
        """
        ansatz = TwoLocal(
            num_qubits=self.num_qubits,
            rotation_blocks=['ry', 'rz'],  # Single-qubit rotations
            entanglement_blocks='cx',       # CNOT for entanglement
            entanglement='linear',
            reps=reps,
            insert_barriers=True
        )
        
        num_params = ansatz.num_parameters
        print(f"✓ TwoLocal ansatz created:")
        print(f"  - Repetitions: {reps}")
        print(f"  - Rotation gates: RY, RZ")
        print(f"  - Entanglement: CNOT (linear)")
        print(f"  - Total parameters: {num_params}")
        print(f"  - Circuit depth: ~{ansatz.depth()}")
        
        return ansatz
    
    def create_custom_protein_ansatz(self, reps=2):
        """
        Creates a custom ansatz optimized for protein folding.
        Uses structure inspired by protein geometry constraints.
        
        Args:
            reps: Number of repetitions
        """
        qc = QuantumCircuit(self.num_qubits)
        params = ParameterVector('θ', length=self.num_qubits * reps * 2)
        param_idx = 0
        
        for rep in range(reps):
            # Rotation layer - each qubit rotates independently
            for qubit in range(self.num_qubits):
                qc.ry(params[param_idx], qubit)
                param_idx += 1
            
            # Entanglement layer - pairs of qubits (representing turns)
            for qubit in range(0, self.num_qubits - 1, 2):
                qc.cx(qubit, qubit + 1)
            
            # Second rotation layer
            for qubit in range(self.num_qubits):
                qc.rz(params[param_idx], qubit)
                param_idx += 1
            
            # Additional entanglement for neighboring turns
            for qubit in range(1, self.num_qubits - 1, 2):
                qc.cx(qubit, qubit + 1)
            
            qc.barrier()
        
        print(f"✓ Custom protein ansatz created:")
        print(f"  - Repetitions: {reps}")
        print(f"  - Total parameters: {len(params)}")
        print(f"  - Circuit depth: ~{qc.depth()}")
        print(f"  - Designed for protein turn representation")
        
        return qc, params
    
    def build_complete_circuit(self, ansatz_type='efficient_su2', reps=3):
        """
        Builds the complete quantum circuit with initial state + ansatz.
        
        Args:
            ansatz_type: 'efficient_su2', 'twolocal', or 'custom'
            reps: Number of repetitions
        """
        print("\n" + "="*60)
        print("QUANTUM CIRCUIT DESIGN")
        print("="*60)
        print(f"Number of qubits: {self.num_qubits}")
        print(f"Ansatz type: {ansatz_type}")
        print()
        
        # Create initial state
        init_state = self.create_initial_state()
        
        # Create ansatz based on type
        if ansatz_type == 'efficient_su2':
            ansatz = self.create_efficient_su2_ansatz(reps)
            self.circuit = init_state.compose(ansatz)
            self.parameters = ansatz.parameters
            
        elif ansatz_type == 'twolocal':
            ansatz = self.create_twolocal_ansatz(reps)
            self.circuit = init_state.compose(ansatz)
            self.parameters = ansatz.parameters
            
        elif ansatz_type == 'custom':
            ansatz, params = self.create_custom_protein_ansatz(reps)
            self.circuit = init_state.compose(ansatz)
            self.parameters = params
            
        else:
            raise ValueError(f"Unknown ansatz type: {ansatz_type}")
        
        # Add measurements
        self.circuit.measure_all()
        
        print("\n✓ Complete circuit assembled!")
        print(f"  - Total gates: {sum(self.circuit.count_ops().values())}")
        print(f"  - Circuit depth: {self.circuit.depth()}")
        print(f"  - Parameters to optimize: {len(self.parameters)}")
        print("="*60)
        
        return self.circuit, self.parameters
    
    def get_circuit_info(self):
        """
        Returns detailed information about the circuit.
        """
        if self.circuit is None:
            return "Circuit not yet built. Call build_complete_circuit() first."
        
        info = {
            'num_qubits': self.num_qubits,
            'num_parameters': len(self.parameters),
            'circuit_depth': self.circuit.depth(),
            'gate_counts': dict(self.circuit.count_ops()),
            'total_gates': sum(self.circuit.count_ops().values())
        }
        return info
    
    def visualize_circuit(self, output_file='protein_circuit.png'):
        """
        Saves a visualization of the circuit (first few layers).
        """
        if self.circuit is None:
            print("Build circuit first!")
            return
        
        # For large circuits, show only first few layers
        if self.circuit.depth() > 20:
            print(f"Circuit is large (depth: {self.circuit.depth()})")
            print("Drawing first portion only...")
        
        try:
            fig = self.circuit.draw(output='mpl', fold=20)
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✓ Circuit diagram saved to: {output_file}")
        except Exception as e:
            print(f"Visualization skipped (circuit too large): {e}")

# Example usage:
if __name__ == "__main__":
    from step2_lattice_encoding import ProteinLatticeEncoder
    from step3_hamiltonian import ProteinHamiltonianBuilder
    
    # Get sequence and build previous steps
    validated_sequence = input("Enter your validated amino acid sequence: ")
    
    # Step 2: Encode sequence
    encoder = ProteinLatticeEncoder(validated_sequence)
    lattice_info = encoder.get_lattice_info()
    
    # Step 3: Build Hamiltonian
    hamiltonian_builder = ProteinHamiltonianBuilder(
        encoded_sequence=lattice_info['encoded_sequence'],
        num_qubits=lattice_info['num_qubits'],
        lattice_info=lattice_info
    )
    hamiltonian_info = hamiltonian_builder.construct_hamiltonian()
    
    # Step 4: Design Quantum Circuit
    circuit_designer = ProteinQuantumCircuit(
        num_qubits=lattice_info['num_qubits'],
        hamiltonian_info=hamiltonian_info
    )
    
    # Choose ansatz type: 'efficient_su2', 'twolocal', or 'custom'
    ansatz_choice = 'efficient_su2'  # Change this to try different ansatzes
    repetitions = 3  # Increase for more expressive circuits
    
    circuit, parameters = circuit_designer.build_complete_circuit(
        ansatz_type=ansatz_choice,
        reps=repetitions
    )
    
    # Display circuit information
    print("\nCircuit Information:")
    print(circuit_designer.get_circuit_info())
    
    # Optionally save circuit diagram
    # circuit_designer.visualize_circuit('my_protein_circuit.png')
    
    print("\n✓ Quantum circuit design complete!")
    print("Ready for VQE optimization in Step 5")
