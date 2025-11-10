# 🧬⚛️ Quantum Protein Structure Predictor

A production-ready quantum computing system for predicting protein structures using the Variational Quantum Eigensolver (VQE) algorithm on a tetrahedral lattice model.

## 🌟 Overview

This project implements a complete end-to-end pipeline for protein structure prediction using quantum computing, specifically designed for near-term quantum hardware (NISQ devices).

### Key Features

- ✅ **6-Step Pipeline**: Validation → Encoding → Hamiltonian → Circuit → VQE → Visualization
- ⚛️ **Quantum Algorithm**: VQE with multiple ansatz options
- 🧬 **Physics-Based**: Miyazawa-Jernigan hydrophobicity model
- 📊 **Professional Output**: PDB files, 3D visualizations, JSON reports
- 🚀 **Production-Ready**: Batch processing, error handling, logging

## 📋 Requirements

### Python Dependencies

```bash
pip install qiskit qiskit-algorithms qiskit-optimization numpy matplotlib
```

### Tested Environment

- Python 3.13.3
- Qiskit 2.2.1
- Windows/Linux/macOS compatible

## ⚠️ Important: Sequence Length Limits

**Classical simulation is limited by available memory:**

| Sequence Length | Qubits | Memory | Status |
|----------------|--------|--------|--------|
| 3-7 residues | 4-12 | <16 MB | ✅ **Recommended** |
| 8-10 residues | 14-18 | 64-512 MB | ⚠️ Requires 8-16 GB RAM |
| 11-15 residues | 20-28 | 8-64 GB | ⚠️ Workstation only |
| 20+ residues | 38+ | >4 TB | ❌ **Impossible on classical** |

**For longer sequences:** Use IBM Quantum hardware (free account available) or tensor network simulators. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for details.

## 🚀 Quick Start

### Single Sequence Prediction

```bash
python quantum_protein_predictor.py
```

Select option 1, enter your sequence (e.g., `ACDE` or `GYL`), and press Enter for default settings.

**Recommended test sequences:** GYL, ACDE, FGHIK, ACDEFGH

### Programmatic Usage

```python
from quantum_protein_predictor import QuantumProteinPredictor

predictor = QuantumProteinPredictor()
result = predictor.predict_structure(
    sequence="ACDE",  # Use 3-7 residues for best performance
    ansatz_type="efficient_su2",
    optimizer="COBYLA",
    max_iter=50,
    reps=2,
    output_dir="results"
)

print(f"Energy: {result['energy']:.6f}")
print(f"Valid: {result['valid_structure']}")
```

### Batch Processing

```python
sequences = ["GYL", "ACDE", "FGHK"]
results = predictor.batch_predict(sequences)
```

## 📁 Project Structure

```
Qiskit/
├── quantum_protein_predictor.py  # Main production interface
├── step1_validation.py           # Sequence validation
├── step2_lattice_encoding.py     # Tetrahedral lattice encoding
├── step3_hamiltonian.py          # Energy function construction
├── step4_quantum_circuit.py      # Quantum ansatz design
├── step5_vqe_optimization.py     # VQE optimization
├── step6_structure_visualization.py  # 3D structure decoding
└── results/                      # Output directory
    ├── {SEQUENCE}_structure.pdb
    ├── {SEQUENCE}_structure_3d.png
    ├── {SEQUENCE}_convergence.png
    └── {SEQUENCE}_report.json
```

## 🔬 Algorithm Details

### Step 1: Validation
- Checks for valid amino acid codes (20 standard amino acids)
- Enforces length limit (max 20 residues for current hardware)
- Input sanitization

### Step 2: Lattice Encoding
- Maps protein to tetrahedral lattice (4 directions)
- Each turn encoded with 2 qubits
- Assigns Miyazawa-Jernigan hydrophobicity values

### Step 3: Hamiltonian Construction
- **Chirality constraints**: Enforces correct stereochemistry
- **Geometry constraints**: Maintains bond lengths/angles
- **Overlap prevention**: Prevents atom collisions
- **Interaction energy**: Models hydrophobic effect

### Step 4: Quantum Circuit Design
Three ansatz options:
1. **EfficientSU2**: Hardware-efficient, good expressibility
2. **TwoLocal**: Customizable rotations (RY, RZ) + CNOT
3. **Custom**: Protein-specific architecture

### Step 5: VQE Optimization
Four optimizer options:
- **COBYLA**: Constrained optimization (gradient-free)
- **SPSA**: Stochastic approximation
- **SLSQP**: Sequential least squares
- **L-BFGS-B**: Quasi-Newton method

### Step 6: Structure Decoding
- Converts quantum state to 3D coordinates
- Validates structure (no overlaps)
- Calculates radius of gyration
- Exports PDB and visualizations

## 📊 Output Files

### 1. PDB File (`{SEQUENCE}_structure.pdb`)
Standard Protein Data Bank format:
- Compatible with PyMOL, VMD, Chimera
- C-alpha backbone representation
- Scaled coordinates (3.8 Å per lattice unit)

**View in PyMOL:**
```bash
pymol results/ACDE_structure.pdb
```

### 2. 3D Visualization (`{SEQUENCE}_structure_3d.png`)
High-resolution matplotlib plot:
- Color-coded by hydrophobicity
  - 🔴 Red: Hydrophobic (>1.0)
  - 🔵 Blue: Hydrophilic (<0)
  - 🟢 Green: Neutral
- Labeled amino acids
- Connected backbone

### 3. Convergence Plot (`{SEQUENCE}_convergence.png`)
Energy vs. iteration:
- Shows optimization trajectory
- Validates convergence

### 4. JSON Report (`{SEQUENCE}_report.json`)
Comprehensive metadata:
```json
{
  "sequence": "ACDE",
  "energy": -22.554241,
  "qubits": 6,
  "valid_structure": true,
  "radius_of_gyration": 1.369,
  "timestamp": "2025-10-20T18:25:30"
}
```

## 🎯 Example Results

### Sequence: GYL (Glycine-Tyrosine-Leucine)
- **Qubits**: 4
- **Energy**: -22.83
- **Structure**: Valid, compact (Rg = 0.82 Å)
- **Time**: 0.23 seconds

### Sequence: ACDE (Ala-Cys-Asp-Glu)
- **Qubits**: 6
- **Energy**: -22.55
- **Structure**: Valid (Rg = 1.37 Å)
- **Time**: 0.25 seconds

## 🔧 Configuration

### Ansatz Selection
- `efficient_su2`: Best for most sequences (balanced)
- `twolocal`: More flexible, longer circuits
- `custom`: Protein-specific, experimental

### Optimizer Selection
- `COBYLA`: Reliable, gradient-free (recommended)
- `SPSA`: Faster for noisy simulations
- `SLSQP`: Better for smooth landscapes
- `L_BFGS_B`: Quasi-Newton, fewer iterations

### Performance Tuning
- **reps**: Circuit depth (2-4 recommended)
- **max_iter**: VQE iterations (50-100 typical)
- Increase for longer sequences or better accuracy

## 📚 Scientific Background

### Protein Folding Problem
Proteins fold to minimize free energy. Finding the native structure is NP-hard, making it ideal for quantum computing.

### Lattice Models
Simplified representation where amino acids occupy discrete lattice sites. Reduces complexity while preserving key physics.

### VQE Algorithm
Hybrid quantum-classical algorithm:
1. Quantum computer prepares trial state
2. Classical computer measures energy
3. Optimizer adjusts parameters
4. Repeat until convergence

### Miyazawa-Jernigan Potential
Statistical potential derived from known protein structures, capturing hydrophobic interactions.

## ⚠️ Limitations

- **Sequence length**: Currently limited to 20 residues (hardware constraints)
- **Lattice approximation**: Simplified vs. all-atom models
- **Classical simulation**: Not running on real quantum hardware
- **Simplified energy**: Missing electrostatics, hydrogen bonds

## 🚀 Future Enhancements

- [ ] Integration with IBM Quantum hardware
- [ ] QAOA optimization algorithm
- [ ] Side-chain modeling
- [ ] Multi-objective optimization (energy + compactness)
- [ ] Sequence database integration
- [ ] Web interface

## 📖 References

1. Perdomo-Ortiz et al. (2012) - "Finding low-energy conformations of lattice protein models by quantum annealing"
2. Robert et al. (2019) - "Resource-efficient quantum algorithm for protein folding"
3. Miyazawa & Jernigan (1996) - "Residue-residue potentials with a favorable contact pair term"

## 🤝 Contributing

Contributions welcome! Areas of interest:
- New ansatz designs
- Better energy functions
- Hardware integration
- Performance optimization

## 📄 License

MIT License - Feel free to use for research and education.

## 👥 Authors

Created with GitHub Copilot assistance.

## 🙏 Acknowledgments

- IBM Qiskit team for quantum computing framework
- Protein folding research community
- Quantum algorithms research community

---

**Note**: This is a research tool for educational purposes. For production protein structure prediction, use established tools like AlphaFold, Rosetta, or MODELLER.

## 📞 Support

For questions or issues:
1. Check existing documentation
2. Review example outputs in `results/`
3. Verify dependencies are installed
4. Check Python version compatibility

---

**Happy Quantum Computing! 🧬⚛️**
