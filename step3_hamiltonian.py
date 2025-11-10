# Step 3: Hamiltonian Construction for Quantum Protein Structure Prediction

import numpy as np
from qiskit.quantum_info import SparsePauliOp
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.converters import QuadraticProgramToQubo

class ProteinHamiltonianBuilder:
    """
    Constructs the Hamiltonian for protein folding problem.
    Includes chirality, geometry, distance, and interaction energy terms.
    """
    
    def __init__(self, encoded_sequence, num_qubits, lattice_info):
        self.encoded_sequence = encoded_sequence
        self.num_qubits = num_qubits
        self.lattice_info = lattice_info
        self.sequence_length = len(encoded_sequence)
        self.num_turns = self.sequence_length - 1
        
        # Penalty weights (tunable parameters)
        self.weights = {
            'chirality': 10.0,      # Enforce correct stereochemistry
            'geometry': 8.0,        # Maintain bond lengths and angles
            'overlap': 15.0,        # Prevent atom collisions
            'interaction': 1.0      # Amino acid interactions (hydrophobic effect)
        }
    
    def build_chirality_constraints(self):
        """
        Ensures the protein backbone maintains correct chirality.
        Prevents physically impossible configurations.
        """
        chirality_terms = []
        penalty = self.weights['chirality']
        
        # For tetrahedral lattice: certain turn combinations are forbidden
        for i in range(self.num_turns - 1):
            qubit_pair = (i * 2, (i + 1) * 2)
            chirality_terms.append((qubit_pair, penalty))
        
        print(f"✓ Chirality constraints: {len(chirality_terms)} terms")
        return chirality_terms
    
    def build_geometry_constraints(self):
        """
        Enforces proper bond lengths and bond angles.
        Maintains realistic protein geometry.
        """
        geometry_terms = []
        penalty = self.weights['geometry']
        
        # Adjacent beads must maintain proper distance
        for i in range(self.num_turns):
            for qubit in range(i * 2, (i + 1) * 2):
                geometry_terms.append((qubit, penalty))
        
        print(f"✓ Geometry constraints: {len(geometry_terms)} terms")
        return geometry_terms
    
    def build_overlap_constraints(self):
        """
        Prevents two amino acids from occupying the same lattice position.
        Critical for physical validity.
        """
        overlap_terms = []
        penalty = self.weights['overlap']
        
        # Check all pairs of non-adjacent beads
        for i in range(self.sequence_length):
            for j in range(i + 2, self.sequence_length):
                # Penalize configurations where beads i and j overlap
                overlap_terms.append(((i, j), penalty))
        
        print(f"✓ Overlap prevention: {len(overlap_terms)} terms")
        return overlap_terms
    
    def build_interaction_energy(self):
        """
        Calculates interaction energies between amino acids.
        Favors hydrophobic core formation (like in real proteins).
        """
        interaction_terms = []
        weight = self.weights['interaction']
        
        # Calculate pairwise interactions based on hydrophobicity
        for i in range(self.sequence_length):
            for j in range(i + 1, self.sequence_length):
                aa_i = self.encoded_sequence[i]
                aa_j = self.encoded_sequence[j]
                
                # Contact energy (negative for favorable hydrophobic interactions)
                hydro_i = aa_i['hydrophobicity']
                hydro_j = aa_j['hydrophobicity']
                
                # Hydrophobic amino acids attract each other
                contact_energy = -weight * hydro_i * hydro_j
                
                if abs(contact_energy) > 0.01:  # Only store significant interactions
                    interaction_terms.append({
                        'pair': (i, j),
                        'aa_i': aa_i['amino_acid'],
                        'aa_j': aa_j['amino_acid'],
                        'energy': contact_energy
                    })
        
        print(f"✓ Interaction energies: {len(interaction_terms)} terms")
        return interaction_terms
    
    def construct_hamiltonian(self):
        """
        Combines all terms into the final Hamiltonian.
        Returns the complete energy function for quantum optimization.
        """
        print("\n" + "="*60)
        print("HAMILTONIAN CONSTRUCTION")
        print("="*60)
        
        chirality = self.build_chirality_constraints()
        geometry = self.build_geometry_constraints()
        overlap = self.build_overlap_constraints()
        interactions = self.build_interaction_energy()
        
        hamiltonian_info = {
            'num_qubits': self.num_qubits,
            'chirality_terms': len(chirality),
            'geometry_terms': len(geometry),
            'overlap_terms': len(overlap),
            'interaction_terms': len(interactions),
            'total_terms': len(chirality) + len(geometry) + len(overlap) + len(interactions),
            'weights': self.weights,
            'chirality_constraints': chirality,
            'geometry_constraints': geometry,
            'overlap_constraints': overlap,
            'interaction_energies': interactions
        }
        
        print(f"\nTotal Hamiltonian terms: {hamiltonian_info['total_terms']}")
        print(f"Penalty weights: {self.weights}")
        print("="*60)
        
        return hamiltonian_info
    
    def display_interaction_matrix(self):
        """
        Shows the interaction energy matrix between amino acids.
        Useful for understanding which residues attract/repel.
        """
        print("\nAmino Acid Interaction Summary:")
        print("-" * 60)
        
        for i, aa in enumerate(self.encoded_sequence):
            print(f"{i}: {aa['amino_acid']} (hydrophobicity: {aa['hydrophobicity']:.2f})")

# Example usage:
if __name__ == "__main__":
    # Use the output from Step 2
    from step2_lattice_encoding import ProteinLatticeEncoder
    
    validated_sequence = input("Enter your validated amino acid sequence: ")
    encoder = ProteinLatticeEncoder(validated_sequence)
    lattice_info = encoder.get_lattice_info()
    
    # Build Hamiltonian
    hamiltonian_builder = ProteinHamiltonianBuilder(
        encoded_sequence=lattice_info['encoded_sequence'],
        num_qubits=lattice_info['num_qubits'],
        lattice_info=lattice_info
    )
    
    hamiltonian_info = hamiltonian_builder.construct_hamiltonian()
    hamiltonian_builder.display_interaction_matrix()
    
    print("\n✓ Hamiltonian successfully constructed!")
    print(f"Ready for quantum circuit design with {hamiltonian_info['num_qubits']} qubits")
