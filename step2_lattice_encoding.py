# Step 2: Sequence Encoding & Lattice Mapping for Quantum Protein Structure Prediction

import numpy as np
from itertools import product

class ProteinLatticeEncoder:
    """
    Encodes a protein sequence onto a tetrahedral lattice for quantum simulation.
    Each amino acid is a bead on the lattice with possible turn directions.
    """
    
    def __init__(self, sequence):
        self.sequence = sequence.upper()
        self.length = len(sequence)
        
        # Tetrahedral lattice: 4 possible directions from each point
        # Directions: [0, 1, 2, 3] representing different spatial orientations
        self.num_turns = self.length - 1  # n-1 turns for n amino acids
        self.possible_directions = 4  # Tetrahedral lattice
        
        # Map amino acids to interaction parameters (simplified Miyazawa-Jernigan)
        self.amino_acid_properties = {
            'A': 0.5, 'C': 1.0, 'D': -0.8, 'E': -0.8, 'F': 1.2,
            'G': 0.0, 'H': 0.5, 'I': 1.8, 'K': -0.9, 'L': 1.8,
            'M': 1.3, 'N': -0.2, 'P': 0.0, 'Q': -0.2, 'R': -0.9,
            'S': -0.3, 'T': 0.4, 'V': 1.5, 'W': 0.9, 'Y': 0.7
        }
    
    def encode_sequence(self):
        """
        Encodes the sequence with its hydrophobic/hydrophilic properties.
        Returns encoded sequence with interaction weights.
        """
        encoded = []
        for aa in self.sequence:
            encoded.append({
                'amino_acid': aa,
                'hydrophobicity': self.amino_acid_properties.get(aa, 0.0)
            })
        return encoded
    
    def calculate_num_qubits(self):
        """
        Calculate number of qubits needed.
        Each turn requires log2(4) = 2 qubits for tetrahedral lattice.
        """
        qubits_per_turn = 2  # 2 qubits encode 4 directions
        total_qubits = self.num_turns * qubits_per_turn
        return total_qubits
    
    def get_lattice_info(self):
        """
        Returns information about the lattice mapping.
        """
        return {
            'sequence': self.sequence,
            'length': self.length,
            'num_turns': self.num_turns,
            'num_qubits': self.calculate_num_qubits(),
            'lattice_type': 'Tetrahedral',
            'directions_per_turn': self.possible_directions,
            'encoded_sequence': self.encode_sequence()
        }

# Example usage:
if __name__ == "__main__":
    # Load the validated sequence from Step 1
    validated_sequence = input("Enter the validated amino acid sequence from Step 1: ")
    
    encoder = ProteinLatticeEncoder(validated_sequence)
    lattice_info = encoder.get_lattice_info()
    
    print("\n" + "="*60)
    print("LATTICE MAPPING INFORMATION")
    print("="*60)
    print(f"Sequence: {lattice_info['sequence']}")
    print(f"Length: {lattice_info['length']} amino acids")
    print(f"Number of turns: {lattice_info['num_turns']}")
    print(f"Qubits required: {lattice_info['num_qubits']}")
    print(f"Lattice type: {lattice_info['lattice_type']}")
    print(f"Directions per turn: {lattice_info['directions_per_turn']}")
    print("\nEncoded Sequence with Properties:")
    for i, aa_info in enumerate(lattice_info['encoded_sequence']):
        print(f"  Position {i}: {aa_info['amino_acid']} (Hydrophobicity: {aa_info['hydrophobicity']})")
    print("="*60)
