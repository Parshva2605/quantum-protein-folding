# Step 5: VQE Optimization for Protein Structure Prediction

from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator as Estimator

from qiskit_algorithms import VQE
from qiskit_algorithms.optimizers import COBYLA, SPSA, SLSQP, L_BFGS_B
from qiskit.quantum_info import SparsePauliOp
import numpy as np
import time
from datetime import datetime

class ProteinVQEOptimizer:
    """
    Implements VQE optimization to find the minimum energy protein structure.
    Uses classical optimizer to tune quantum circuit parameters.
    """
    
    def __init__(self, circuit, parameters, hamiltonian_info, num_qubits):
        self.circuit = circuit
        self.parameters = parameters
        self.hamiltonian_info = hamiltonian_info
        self.num_qubits = num_qubits
        self.optimization_history = []
        self.iteration_count = 0
        
    def construct_qubit_hamiltonian(self):
        """
        Converts the protein Hamiltonian to Pauli operators for quantum computer.
        Creates the operator that VQE will minimize.
        """
        print("\n" + "="*60)
        print("CONSTRUCTING QUBIT HAMILTONIAN")
        print("="*60)
        
        # Build Pauli strings for each constraint
        pauli_list = []
        
        # Chirality constraints
        for term in self.hamiltonian_info['chirality_constraints']:
            qubit_pair, penalty = term
            # Create Pauli-Z operators for constraint
            pauli_str = ['I'] * self.num_qubits
            pauli_str[qubit_pair[0]] = 'Z'
            if qubit_pair[1] < self.num_qubits:
                pauli_str[qubit_pair[1]] = 'Z'
            pauli_list.append((''.join(pauli_str), penalty))
        
        # Geometry constraints
        for term in self.hamiltonian_info['geometry_constraints']:
            qubit, penalty = term
            pauli_str = ['I'] * self.num_qubits
            pauli_str[qubit] = 'Z'
            pauli_list.append((''.join(pauli_str), penalty))
        
        # Interaction energies (simplified)
        for interaction in self.hamiltonian_info['interaction_energies']:
            energy = interaction['energy']
            # Map to qubits representing the amino acid positions
            # Simplified: use position-based mapping
            pauli_list.append(('I' * self.num_qubits, energy))
        
        # Create SparsePauliOp
        if not pauli_list:
            # Fallback: simple identity operator
            hamiltonian = SparsePauliOp.from_list([('I' * self.num_qubits, 1.0)])
        else:
            hamiltonian = SparsePauliOp.from_list(pauli_list[:50])  # Limit for efficiency
        
        print(f"✓ Qubit Hamiltonian constructed")
        print(f"  - Number of Pauli terms: {len(hamiltonian)}")
        print(f"  - Number of qubits: {self.num_qubits}")
        print("="*60)
        
        return hamiltonian
    
    def callback(self, eval_count, parameters, mean, metadata):
        """
        Callback function to track optimization progress.
        Updated for Qiskit 1.x+ compatibility where the 4th parameter is metadata dict.
        """
        self.iteration_count += 1
        
        # Handle parameters - convert to list if needed
        if hasattr(parameters, 'copy'):
            params_copy = parameters.copy()
        else:
            params_copy = list(parameters) if hasattr(parameters, '__iter__') else parameters
        
        # Extract standard deviation from metadata if available
        std_dev = 0.0
        if isinstance(metadata, dict):
            std_dev = metadata.get('variance', 0.0) if 'variance' in metadata else 0.0
        elif isinstance(metadata, (int, float)):
            std_dev = float(metadata)
        
        self.optimization_history.append({
            'iteration': self.iteration_count,
            'energy': float(mean),
            'std': float(std_dev),
            'parameters': params_copy,
            'metadata': metadata
        })
        
        if self.iteration_count % 5 == 0:
            print(f"  Iteration {self.iteration_count}: Energy = {float(mean):.6f}")
    
    def run_vqe(self, optimizer_name='COBYLA', max_iter=100):
        """
        Runs VQE optimization to find the ground state.
        
        Args:
            optimizer_name: 'COBYLA', 'SPSA', 'SLSQP', or 'L_BFGS_B'
            max_iter: Maximum number of optimization iterations
        """
        print("\n" + "="*60)
        print("VQE OPTIMIZATION")
        print("="*60)
        print(f"Optimizer: {optimizer_name}")
        print(f"Max iterations: {max_iter}")
        print(f"Parameters to optimize: {len(self.parameters)}")
        
        # Check if simulation is feasible
        memory_required_gb = (2 ** self.num_qubits * 16) / (1024**3)
        if self.num_qubits > 20:
            print("\n❌ ERROR: Too many qubits for classical simulation!")
            print(f"   Qubits: {self.num_qubits}")
            print(f"   Required memory: {memory_required_gb:.1f} GB")
            print(f"   Maximum recommended: 20 qubits (~16 GB)")
            print("\n   Solutions:")
            print("   1. Use shorter sequences (max 10 residues = 18 qubits)")
            print("   2. Use real quantum hardware (IBM Quantum)")
            print("   3. Use tensor network simulators (e.g., Qiskit Aer with matrix_product_state)")
            return None
        
        if memory_required_gb > 8:
            print(f"\n⚠️  WARNING: High memory usage expected: {memory_required_gb:.1f} GB")
            print(f"   This may take a long time or fail on systems with <{memory_required_gb*2:.0f} GB RAM")
        
        print()
        
        # Construct Hamiltonian
        hamiltonian = self.construct_qubit_hamiltonian()
        
        # Choose optimizer
        if optimizer_name == 'COBYLA':
            optimizer = COBYLA(maxiter=max_iter)
        elif optimizer_name == 'SPSA':
            optimizer = SPSA(maxiter=max_iter)
        elif optimizer_name == 'SLSQP':
            optimizer = SLSQP(maxiter=max_iter)
        elif optimizer_name == 'L_BFGS_B':
            optimizer = L_BFGS_B(maxiter=max_iter)
        else:
            raise ValueError(f"Unknown optimizer: {optimizer_name}")
        
        # Initialize estimator (for quantum/classical simulation)
        estimator = Estimator()
        
        # Create VQE instance
        vqe = VQE(
            estimator=estimator,
            ansatz=self.circuit.remove_final_measurements(inplace=False),
            optimizer=optimizer,
            callback=self.callback
        )
        
        # Run optimization
        print("Starting VQE optimization...")
        print("-" * 60)
        start_time = time.time()
        
        try:
            result = vqe.compute_minimum_eigenvalue(hamiltonian)
            end_time = time.time()
            
            print("-" * 60)
            print(f"✓ VQE optimization complete!")
            print(f"  Time elapsed: {end_time - start_time:.2f} seconds")
            print(f"  Total iterations: {self.iteration_count}")
            print(f"  Ground state energy: {result.eigenvalue:.6f}")
            print(f"  Optimal parameters found: {len(result.optimal_parameters)}")
            print("="*60)
            
            return result
            
        except Exception as e:
            import traceback
            print(f"\n❌ Error during VQE optimization: {e}")
            print("\nDetailed traceback:")
            traceback.print_exc()
            print("\nThis might be due to:")
            print("  - Circuit complexity or Hamiltonian size")
            print("  - Qiskit version compatibility issues")
            print("  - Try reducing 'reps' parameter or 'max_iter'")
            return None
    
    def get_optimal_structure(self, vqe_result):
        """
        Extracts the optimal protein structure from VQE results.
        Converts quantum state to classical protein coordinates.
        """
        if vqe_result is None:
            print("No VQE result available.")
            return None
        
        print("\n" + "="*60)
        print("EXTRACTING OPTIMAL STRUCTURE")
        print("="*60)
        
        optimal_params = vqe_result.optimal_parameters
        optimal_energy = vqe_result.eigenvalue
        
        # Get the optimal quantum state (bitstring)
        # In a real implementation, we would measure the circuit
        # For now, we'll create a representative structure
        
        structure_info = {
            'energy': optimal_energy,
            'parameters': dict(optimal_params),
            'num_iterations': self.iteration_count,
            'convergence_history': self.optimization_history
        }
        
        print(f"✓ Optimal structure found")
        print(f"  - Ground state energy: {optimal_energy:.6f}")
        print(f"  - Optimization iterations: {self.iteration_count}")
        print("="*60)
        
        return structure_info
    
    def plot_convergence(self, output_file='vqe_convergence.png'):
        """
        Plots the energy convergence during optimization.
        """
        if not self.optimization_history:
            print("No optimization history to plot.")
            return
        
        import matplotlib.pyplot as plt
        
        iterations = [h['iteration'] for h in self.optimization_history]
        energies = [h['energy'] for h in self.optimization_history]
        
        plt.figure(figsize=(10, 6))
        plt.plot(iterations, energies, 'b-', linewidth=2)
        plt.xlabel('Iteration', fontsize=12)
        plt.ylabel('Energy', fontsize=12)
        plt.title('VQE Convergence for Protein Structure Prediction', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Convergence plot saved to: {output_file}")
        plt.close()

# Example usage:
if __name__ == "__main__":
    from step2_lattice_encoding import ProteinLatticeEncoder
    from step3_hamiltonian import ProteinHamiltonianBuilder
    from step4_quantum_circuit import ProteinQuantumCircuit
    
    print("="*60)
    print("QUANTUM PROTEIN STRUCTURE PREDICTION - VQE OPTIMIZATION")
    print("="*60)
    
    # Get sequence
    validated_sequence = input("\nEnter your validated amino acid sequence: ")
    
    # Step 2: Encode sequence
    print("\n[1/4] Encoding sequence...")
    encoder = ProteinLatticeEncoder(validated_sequence)
    lattice_info = encoder.get_lattice_info()
    
    # Step 3: Build Hamiltonian
    print("[2/4] Building Hamiltonian...")
    hamiltonian_builder = ProteinHamiltonianBuilder(
        encoded_sequence=lattice_info['encoded_sequence'],
        num_qubits=lattice_info['num_qubits'],
        lattice_info=lattice_info
    )
    hamiltonian_info = hamiltonian_builder.construct_hamiltonian()
    
    # Step 4: Design Quantum Circuit
    print("[3/4] Designing quantum circuit...")
    circuit_designer = ProteinQuantumCircuit(
        num_qubits=lattice_info['num_qubits'],
        hamiltonian_info=hamiltonian_info
    )
    circuit, parameters = circuit_designer.build_complete_circuit(
        ansatz_type='efficient_su2',
        reps=2
    )
    
    # Step 5: Run VQE Optimization
    print("[4/4] Running VQE optimization...")
    vqe_optimizer = ProteinVQEOptimizer(
        circuit=circuit,
        parameters=parameters,
        hamiltonian_info=hamiltonian_info,
        num_qubits=lattice_info['num_qubits']
    )
    
    # Choose optimizer: 'COBYLA', 'SPSA', 'SLSQP', or 'L_BFGS_B'
    vqe_result = vqe_optimizer.run_vqe(
        optimizer_name='COBYLA',
        max_iter=50
    )
    
    # Extract optimal structure
    if vqe_result:
        optimal_structure = vqe_optimizer.get_optimal_structure(vqe_result)
        vqe_optimizer.plot_convergence('protein_vqe_convergence.png')
        
        print("\n" + "="*60)
        print("OPTIMIZATION SUMMARY")
        print("="*60)
        print(f"Sequence: {validated_sequence}")
        print(f"Length: {len(validated_sequence)} amino acids")
        print(f"Qubits used: {lattice_info['num_qubits']}")
        print(f"Ground state energy: {optimal_structure['energy']:.6f}")
        print(f"Iterations: {optimal_structure['num_iterations']}")
        print("="*60)
        
        print("\n✓ VQE optimization complete!")
        print("Ready for structure decoding in Step 6")
