# Step 1: User Input & Validation for Quantum Protein Structure Prediction

# List of valid amino acid one-letter codes
valid_amino_acids = set("ACDEFGHIKLMNPQRSTVWY")

def validate_sequence(seq):
    """
    Validates the input amino acid sequence.
    Returns True if valid, False otherwise.
    """
    seq = seq.strip().upper()
    if not seq:
        return False, "Sequence is empty."
    for c in seq:
        if c not in valid_amino_acids:
            return False, f"Invalid amino acid code found: {c}"
    if len(seq) > 20:
        return False, "Sequence too long for current quantum hardware (max 20 residues)."
    
    # Warn about simulation limits
    num_qubits = (len(seq) - 1) * 2
    if len(seq) > 10:
        memory_gb = (2 ** num_qubits * 16) / (1024**3)
        return False, (f"Sequence too long for classical simulation ({len(seq)} residues = {num_qubits} qubits).\n"
                      f"       Required memory: {memory_gb:.1f} GB. Maximum recommended: 8 residues (14 qubits).\n"
                      f"       For longer sequences, use real quantum hardware or tensor network simulators.")
    
    return True, "Sequence is valid."

# Example usage:
if __name__ == "__main__":
    user_sequence = input("Enter your amino acid sequence (max 20 residues, one-letter codes): ")
    is_valid, message = validate_sequence(user_sequence)
    print(message)
    
    if is_valid:
        print(f"Your sequence: {user_sequence.strip().upper()}")
        print(f"Sequence length: {len(user_sequence.strip())}")
