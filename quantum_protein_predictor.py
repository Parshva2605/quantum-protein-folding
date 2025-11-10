# PRODUCTION-READY QUANTUM PROTEIN STRUCTURE PREDICTOR
# Complete integrated system with all features

import sys
import os
from datetime import datetime
import json

class QuantumProteinPredictor:
    """
    Production-ready quantum protein structure prediction system.
    Integrates all 6 steps into a unified interface.
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self.results = {}
        
    def predict_structure(self, sequence, 
                         ansatz_type='efficient_su2',
                         optimizer='COBYLA',
                         max_iter=50,
                         reps=2,
                         output_dir='results'):
        """
        Complete end-to-end prediction pipeline.
        
        Args:
            sequence: Amino acid sequence (one-letter codes)
            ansatz_type: 'efficient_su2', 'twolocal', or 'custom'
            optimizer: 'COBYLA', 'SPSA', 'SLSQP', 'L_BFGS_B'
            max_iter: VQE optimization iterations
            reps: Circuit repetitions
            output_dir: Directory for output files
        """
        print("="*70)
        print("🧬 QUANTUM PROTEIN STRUCTURE PREDICTOR v1.0")
        print("="*70)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Sequence: {sequence} ({len(sequence)} residues)")
        print()
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Step 1: Validation
            from step1_validation import validate_sequence
            is_valid, msg = validate_sequence(sequence)
            if not is_valid:
                print(f"❌ Validation failed: {msg}")
                return None
            print(f"✅ Step 1/6: Validation passed")
            
            # Step 2: Encoding
            from step2_lattice_encoding import ProteinLatticeEncoder
            encoder = ProteinLatticeEncoder(sequence)
            lattice_info = encoder.get_lattice_info()
            print(f"✅ Step 2/6: Encoded to {lattice_info['num_qubits']} qubits")
            
            # Step 3: Hamiltonian
            from step3_hamiltonian import ProteinHamiltonianBuilder
            ham_builder = ProteinHamiltonianBuilder(
                lattice_info['encoded_sequence'],
                lattice_info['num_qubits'],
                lattice_info
            )
            ham_info = ham_builder.construct_hamiltonian()
            print(f"✅ Step 3/6: Hamiltonian built ({ham_info['total_terms']} terms)")
            
            # Step 4: Quantum Circuit
            from step4_quantum_circuit import ProteinQuantumCircuit
            circuit_designer = ProteinQuantumCircuit(
                lattice_info['num_qubits'],
                ham_info
            )
            circuit, params = circuit_designer.build_complete_circuit(
                ansatz_type=ansatz_type,
                reps=reps
            )
            print(f"✅ Step 4/6: Circuit designed ({len(params)} parameters)")
            
            # Step 5: VQE Optimization
            from step5_vqe_optimization import ProteinVQEOptimizer
            vqe_opt = ProteinVQEOptimizer(circuit, params, ham_info, lattice_info['num_qubits'])
            vqe_result = vqe_opt.run_vqe(optimizer, max_iter)
            
            if vqe_result is None:
                print("❌ VQE optimization failed")
                return None
                
            optimal_struct = vqe_opt.get_optimal_structure(vqe_result)
            print(f"✅ Step 5/6: VQE converged (E = {optimal_struct['energy']:.6f})")
            
            # Step 6: Structure Decoding
            from step6_structure_visualization import ProteinStructureDecoder
            decoder = ProteinStructureDecoder(sequence, optimal_struct, lattice_info)
            struct_data = decoder.decode_structure()
            
            # Generate outputs
            pdb_file = os.path.join(output_dir, f'{sequence}_structure.pdb')
            viz_file = os.path.join(output_dir, f'{sequence}_structure_3d.png')
            conv_file = os.path.join(output_dir, f'{sequence}_convergence.png')
            
            decoder.export_to_pdb(struct_data, pdb_file)
            decoder.visualize_3d(struct_data, viz_file)
            vqe_opt.plot_convergence(conv_file)
            
            print(f"✅ Step 6/6: Structure decoded and visualized")
            
            # Save metadata
            self.results = {
                'sequence': sequence,
                'length': len(sequence),
                'qubits': lattice_info['num_qubits'],
                'energy': float(optimal_struct['energy']),
                'iterations': optimal_struct['num_iterations'],
                'valid_structure': struct_data['is_valid'],
                'radius_of_gyration': float(struct_data['radius_of_gyration']),
                'ansatz': ansatz_type,
                'optimizer': optimizer,
                'files': {
                    'pdb': pdb_file,
                    'visualization': viz_file,
                    'convergence': conv_file
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # Save JSON report
            json_file = os.path.join(output_dir, f'{sequence}_report.json')
            with open(json_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            
            print("\n" + "="*70)
            print("🎉 PREDICTION COMPLETE!")
            print("="*70)
            print(f"📊 Energy: {self.results['energy']:.6f}")
            print(f"📏 Radius of gyration: {self.results['radius_of_gyration']:.3f} Å")
            print(f"✓ Structure valid: {self.results['valid_structure']}")
            print(f"\n📁 Output files in '{output_dir}/':")
            print(f"   • {sequence}_structure.pdb")
            print(f"   • {sequence}_structure_3d.png")
            print(f"   • {sequence}_convergence.png")
            print(f"   • {sequence}_report.json")
            print("="*70)
            
            return self.results
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def batch_predict(self, sequences, **kwargs):
        """
        Batch prediction for multiple sequences.
        """
        print(f"\n🔄 Batch processing {len(sequences)} sequences...")
        results = {}
        
        for i, seq in enumerate(sequences, 1):
            print(f"\n{'='*70}")
            print(f"Processing {i}/{len(sequences)}: {seq}")
            print(f"{'='*70}")
            result = self.predict_structure(seq, **kwargs)
            results[seq] = result
        
        return results

# Main interface
if __name__ == "__main__":
    predictor = QuantumProteinPredictor()
    
    print("\n" + "="*70)
    print("🧬 QUANTUM PROTEIN STRUCTURE PREDICTOR")
    print("="*70)
    print("\nOptions:")
    print("1. Single sequence prediction")
    print("2. Batch prediction")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        sequence = input("Enter amino acid sequence: ").strip().upper()
        
        # Advanced options
        print("\n⚙️  Advanced settings (press Enter for defaults):")
        ansatz = input("Ansatz type (efficient_su2/twolocal/custom) [efficient_su2]: ").strip() or "efficient_su2"
        optimizer = input("Optimizer (COBYLA/SPSA/SLSQP) [COBYLA]: ").strip() or "COBYLA"
        max_iter = input("Max iterations [50]: ").strip()
        max_iter = int(max_iter) if max_iter else 50
        
        predictor.predict_structure(
            sequence,
            ansatz_type=ansatz,
            optimizer=optimizer,
            max_iter=max_iter
        )
        
    elif choice == "2":
        print("\nEnter sequences (one per line, empty line to finish):")
        sequences = []
        while True:
            seq = input().strip().upper()
            if not seq:
                break
            sequences.append(seq)
        
        if sequences:
            predictor.batch_predict(sequences)
        else:
            print("No sequences entered.")
    
    else:
        print("Goodbye!")
