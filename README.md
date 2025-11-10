# 🧬⚛️ Quantum Protein Structure Predictor

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Qiskit](https://img.shields.io/badge/Qiskit-2.2+-purple.svg)](https://qiskit.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production-success.svg)]()

A production-ready quantum computing system for predicting protein structures using the **Variational Quantum Eigensolver (VQE)** algorithm on a tetrahedral lattice model with an interactive 3D web interface.

## 🌟 Overview

This project implements a complete end-to-end pipeline for protein structure prediction using quantum computing, specifically designed for near-term quantum hardware (NISQ devices). It features a modern web interface with real-time visualization and 360° interactive 3D structure viewer.

### ✨ Key Features

- 🔬 **6-Step Pipeline**: Validation → Encoding → Hamiltonian → Circuit → VQE → Visualization
- ⚛️ **Quantum Algorithm**: VQE with multiple ansatz options (EfficientSU2, TwoLocal, Custom)
- 🧬 **Physics-Based**: Miyazawa-Jernigan hydrophobicity model
- 🌐 **Web Interface**: Real-time predictions with interactive 3D viewer
- 📊 **Professional Output**: PDB files, 3D visualizations, JSON reports
- 🚀 **Production-Ready**: Batch processing, error handling, comprehensive logging
- 🔄 **Interactive 3D**: 360° rotation, multiple rendering styles, color schemes

## 🎥 Demo

```bash
# Start the web interface
python web_app.py

# Open your browser to http://localhost:5000
# Enter a sequence like "ACDEFGH" and watch it predict!
```

## 📋 Requirements

### Python Dependencies

```bash
pip install -r requirements.txt
```

**Core packages:**
- `qiskit >= 2.2.0`
- `qiskit-algorithms >= 0.3.0`
- `qiskit-optimization >= 0.6.0`
- `numpy >= 1.24.0`
- `matplotlib >= 3.7.0`
- `flask >= 3.0.0`

### Tested Environment

- **Python**: 3.13+ (3.10+ supported)
- **Qiskit**: 2.2.1
- **OS**: Windows/Linux/macOS

## ⚠️ Important: Sequence Length Limits

**Classical simulation is limited by available memory:**

| Sequence Length | Qubits | Memory Required | Status | Time |
|----------------|--------|----------------|--------|------|
| 3-5 residues | 4-8 | <1 MB | ✅ **Fast** | <1s |
| 6-7 residues | 10-12 | <16 MB | ✅ **Recommended** | 1-2s |
| 8-10 residues | 14-18 | 64-512 MB | ⚠️ Requires 8+ GB RAM | 2-5s |
| 11-15 residues | 20-28 | 8-64 GB | ⚠️ Workstation only | >10s |
| 20+ residues | 38+ | >4 TB | ❌ **Impossible** | N/A |

**For longer sequences:** Use IBM Quantum hardware (free account at [quantum.ibm.com](https://quantum.ibm.com)) or tensor network simulators.

## 🚀 Quick Start

### Option 1: Web Interface (Recommended)

```bash
python web_app.py
```

Then open **http://localhost:5000** in your browser and:
1. Enter a protein sequence (e.g., `ACDEFGH`)
2. Choose advanced options (optional)
3. Click "Predict Structure"
4. View real-time updates
5. Explore the interactive 3D structure
6. Download results (PDB, images, reports)

### Option 2: Command Line

```bash
python quantum_protein_predictor.py
```

Select option 1, enter your sequence, and follow the prompts.

**Recommended test sequences:** `GYL`, `ACDE`, `FGHIK`, `ACDEFGH`

### Option 3: Programmatic Usage

```python
from quantum_protein_predictor import QuantumProteinPredictor

# Initialize predictor
predictor = QuantumProteinPredictor()

# Predict structure
result = predictor.predict_structure(
    sequence="ACDEFGH",
    ansatz_type="efficient_su2",  # or "twolocal", "custom"
    optimizer="COBYLA",            # or "SPSA", "SLSQP", "L_BFGS_B"
    max_iter=50,
    reps=2,
    output_dir="results"
)

# Access results
print(f"Energy: {result['energy']:.6f}")
print(f"Valid Structure: {result['valid_structure']}")
print(f"Radius of Gyration: {result['radius_of_gyration']:.3f} Å")
```

### Batch Processing

```python
# From file
sequences = ["GYL", "ACDE", "FGHIK", "ACDEFGH"]
results = predictor.batch_predict(sequences)

# Or upload example_sequences.txt via web interface
```

## 📁 Project Structure

```
quantum-protein-folding/
├── 📄 README.md                          # This file
├── 📋 requirements.txt                   # Python dependencies
├── 🌐 web_app.py                         # Flask web server
├── 🔬 quantum_protein_predictor.py       # Main production interface
├── 📊 demo.py                            # Interactive demo script
│
├── 📂 Core Pipeline (6 Steps)
│   ├── step1_validation.py               # Sequence validation
│   ├── step2_lattice_encoding.py         # Tetrahedral lattice encoding
│   ├── step3_hamiltonian.py              # Energy function construction
│   ├── step4_quantum_circuit.py          # Quantum ansatz design
│   ├── step5_vqe_optimization.py         # VQE optimization
│   └── step6_structure_visualization.py  # 3D structure decoding
│
├── 📂 templates/                         # Web interface templates
│   ├── index.html                        # Main page
│   └── viewer.html                       # 3D viewer with rotation
│
├── 📂 Documentation
│   ├── TROUBLESHOOTING.md                # Common issues & solutions
│   ├── PROJECT_SUMMARY.md                # Technical overview
│   ├── ARCHITECTURE.txt                  # System architecture
│   └── CHECKLIST.md                      # Feature completion status
│
├── 📂 examples/
│   └── example_sequences.txt             # Sample sequences for batch upload
│
└── 📂 results/                           # Output directory (auto-created)
    ├── {SEQUENCE}_structure.pdb          # 3D structure (PyMOL compatible)
    ├── {SEQUENCE}_structure_3d.png       # Visualization
    ├── {SEQUENCE}_convergence.png        # VQE optimization plot
    └── {SEQUENCE}_report.json            # Complete metadata
```

## 🔬 Algorithm Details

### Pipeline Overview

```
Input Sequence → Validation → Lattice Encoding → Hamiltonian 
    ↓
3D Structure ← Decoding ← VQE Optimization ← Quantum Circuit
```

### Step 1: Validation
- Checks for valid amino acid codes (20 standard amino acids)
- Enforces length limits based on available memory
- Input sanitization and error reporting

### Step 2: Lattice Encoding
- Maps protein to tetrahedral lattice (4 possible directions per turn)
- Each turn encoded with 2 qubits (log₂(4) = 2)
- Assigns Miyazawa-Jernigan hydrophobicity values to each residue

### Step 3: Hamiltonian Construction
Four energy terms combined:
- **Chirality constraints** (weight: 10.0): Enforces correct stereochemistry
- **Geometry constraints** (weight: 8.0): Maintains bond lengths/angles
- **Overlap prevention** (weight: 15.0): Prevents atom collisions
- **Interaction energy** (weight: 1.0): Models hydrophobic effect

### Step 4: Quantum Circuit Design
Three ansatz architectures:
1. **EfficientSU2**: Hardware-efficient, good expressibility (default)
2. **TwoLocal**: Customizable rotations (RY, RZ) + CNOT entanglement
3. **Custom**: Protein-specific architecture for turn representation

### Step 5: VQE Optimization
Four classical optimizers available:
- **COBYLA**: Constrained optimization, gradient-free (recommended)
- **SPSA**: Stochastic approximation, noise-resistant
- **SLSQP**: Sequential least squares, smooth landscapes
- **L-BFGS-B**: Quasi-Newton method, fewer iterations

Iteratively minimizes energy to find ground state (native structure).

### Step 6: Structure Decoding & Visualization
- Converts quantum bitstring to 3D coordinates
- Validates structure (no overlaps, correct geometry)
- Calculates radius of gyration (compactness metric)
- Exports PDB format and generates visualizations

## 🌐 Web Interface Features

### Main Interface
- ✅ Single sequence input with validation
- ✅ Batch upload from text/CSV files
- ✅ Real-time status updates (polls every 2 seconds)
- ✅ Advanced options: ansatz, optimizer, iterations, reps
- ✅ Example sequences with one-click fill
- ✅ Progress indicators and error messages

### Interactive 3D Viewer
- ✅ **360° Rotation**: Click and drag to rotate
- ✅ **Zoom**: Mouse wheel or buttons
- ✅ **Pan**: Right-click and drag
- ✅ **Auto-rotate**: Toggle automatic rotation
- ✅ **Rendering Styles**: Cartoon, Spheres, Sticks, Lines
- ✅ **Color Schemes**: 
  - Spectrum (rainbow)
  - Chain (single color)
  - Secondary structure
  - **Hydrophobicity** (Red=hydrophobic, Blue=hydrophilic, Green=neutral)
- ✅ **Structure Info**: Energy, radius, iterations, validity

### Download Options
- 📄 **PDB File**: Standard molecular format (PyMOL, VMD, Chimera compatible)
- 🖼️ **2D Image**: High-resolution PNG visualization
- 📈 **Convergence Plot**: VQE energy optimization graph
- 📋 **JSON Report**: Complete prediction metadata

## 📊 Output Files

### 1. PDB File (`{SEQUENCE}_structure.pdb`)
Standard Protein Data Bank format:
- Compatible with PyMOL, VMD, Chimera, Swiss-PdbViewer
- C-alpha backbone representation
- Scaled coordinates (3.8 Å per lattice unit)
- Includes HEADER, TITLE, REMARK with metadata

**View in PyMOL:**
```bash
pymol results/ACDEFGH_structure.pdb
```

### 2. 3D Visualization (`{SEQUENCE}_structure_3d.png`)
High-resolution matplotlib 3D plot:
- Color-coded by hydrophobicity:
  - 🔴 **Red**: Hydrophobic (>1.0) - ILE, VAL, LEU, PHE, TRP
  - 🔵 **Blue**: Hydrophilic (<0) - ASP, GLU, LYS, ARG
  - 🟢 **Green**: Neutral - GLY, SER, THR
- Labeled amino acids with positions
- Connected backbone trace
- Legend and metadata

### 3. Convergence Plot (`{SEQUENCE}_convergence.png`)
Energy vs. iteration graph:
- Shows VQE optimization trajectory
- Validates convergence to ground state
- Useful for parameter tuning

### 4. JSON Report (`{SEQUENCE}_report.json`)
Comprehensive metadata:
```json
{
  "sequence": "ACDEFGH",
  "length": 7,
  "qubits": 12,
  "energy": -43.884330,
  "iterations": 50,
  "valid_structure": true,
  "radius_of_gyration": 1.732,
  "ansatz": "efficient_su2",
  "optimizer": "COBYLA",
  "timestamp": "2025-11-10T18:25:30.123456",
  "files": {
    "pdb": "results/ACDEFGH_structure.pdb",
    "visualization": "results/ACDEFGH_structure_3d.png",
    "convergence": "results/ACDEFGH_convergence.png"
  }
}
```

## 🎯 Example Results

### Sequence: GYL (Glycine-Tyrosine-Leucine)
```
Qubits:        4
Energy:        -22.83
Structure:     Valid, compact
Rg:            0.82 Å
Time:          0.23 seconds
Iterations:    50
```

### Sequence: ACDEFGH (Mixed hydrophobic/hydrophilic)
```
Qubits:        12
Energy:        -43.88
Structure:     Valid
Rg:            1.73 Å
Time:          0.74 seconds
Iterations:    50
```

### Sequence: ACDE (Ala-Cys-Asp-Glu)
```
Qubits:        6
Energy:        -22.55
Structure:     Valid
Rg:            1.37 Å
Time:          0.25 seconds
Iterations:    50
```

## 🔧 Configuration & Tuning

### Ansatz Selection
- **`efficient_su2`**: Best balance of expressibility and circuit depth (default)
- **`twolocal`**: More flexible, longer circuits, higher gate fidelity needed
- **`custom`**: Protein-specific, experimental, optimized for turn representation

### Optimizer Selection
- **`COBYLA`**: Reliable, gradient-free, works well for most sequences (default)
- **`SPSA`**: Faster convergence for noisy simulations, good for hardware
- **`SLSQP`**: Better for smooth energy landscapes, gradient-based
- **`L_BFGS_B`**: Quasi-Newton, fewer iterations, memory-intensive

### Performance Tuning
- **`reps`**: Circuit depth, 2-4 recommended (higher = more expressive but slower)
- **`max_iter`**: VQE iterations, 50-100 typical (increase for better convergence)
- **Memory**: Keep sequences ≤10 residues for fast classical simulation

## 📚 Scientific Background

### Protein Folding Problem
Proteins fold to minimize free energy, forming stable 3D structures essential for biological function. Finding the native structure from sequence is **NP-hard**, making it ideal for quantum computing approaches.

### Lattice Models
Simplified representation where amino acids occupy discrete lattice sites (tetrahedral in this implementation). Reduces complexity from all-atom models while preserving key physics:
- Hydrophobic effect (dominant force)
- Geometric constraints
- Excluded volume

### VQE Algorithm
Hybrid quantum-classical variational algorithm:
1. **Initialize**: Prepare parameterized quantum state |ψ(θ)⟩
2. **Measure**: Calculate energy ⟨ψ(θ)|H|ψ(θ)⟩ on quantum computer
3. **Optimize**: Classical optimizer adjusts θ to minimize energy
4. **Repeat**: Until convergence to ground state

Advantages:
- Noise-resilient (NISQ-friendly)
- Polynomial scaling with system size
- Can escape local minima

### Miyazawa-Jernigan Potential
Statistical contact potential derived from known protein structures in the Protein Data Bank. Captures:
- Hydrophobic interactions (driving force for folding)
- Residue-specific contact preferences
- Empirically validated on real proteins

## ⚠️ Limitations

- **Sequence length**: Currently limited to ~10 residues for classical simulation
- **Lattice approximation**: Simplified geometry vs. all-atom models
- **Missing interactions**: No electrostatics, hydrogen bonds, or solvent effects
- **Classical simulation**: Not running on actual quantum hardware (yet!)
- **Energy function**: Simplified Miyazawa-Jernigan model

## 🚀 Future Enhancements

- [ ] Integration with IBM Quantum hardware via Qiskit Runtime
- [ ] QAOA optimization algorithm implementation
- [ ] Side-chain modeling and rotamer libraries
- [ ] Multi-objective optimization (energy + compactness + similarity)
- [ ] Protein sequence database integration (UniProt, PDB)
- [ ] Comparison with AlphaFold predictions
- [ ] GPU acceleration for classical simulation
- [ ] Docker containerization
- [ ] REST API for programmatic access
- [ ] Advanced visualization (surface, ribbon, electrostatics)

## 📖 References

1. **Perdomo-Ortiz et al. (2012)** - "Finding low-energy conformations of lattice protein models by quantum annealing" - *Nature Scientific Reports*
2. **Robert et al. (2019)** - "Resource-efficient quantum algorithm for protein folding" - *npj Quantum Information*
3. **Miyazawa & Jernigan (1996)** - "Residue-residue potentials with a favorable contact pair term and an unfavorable high packing density term, for simulation and threading" - *Journal of Molecular Biology*
4. **Peruzzo et al. (2014)** - "A variational eigenvalue solver on a photonic quantum processor" - *Nature Communications*
5. **Fingerhuth et al. (2018)** - "A quantum alternating operator ansatz with hard and soft constraints for lattice protein folding" - *arXiv:1810.13411*

## 🤝 Contributing

Contributions are welcome! Areas of interest:
- Novel ansatz designs for protein geometry
- Better classical-quantum hybrid algorithms
- Hardware integration (IBM Quantum, IonQ, Rigetti)
- Performance optimization and parallelization
- Extended energy models (electrostatics, solvation)
- Comparison benchmarks with classical methods

**To contribute:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

Free to use for research, education, and commercial purposes with attribution.

## 👥 Authors

- **Parshva Patel** - Initial work and development
- Created with **GitHub Copilot** assistance

## 🙏 Acknowledgments

- **IBM Qiskit Team** - For the quantum computing framework and documentation
- **Protein Folding Research Community** - For lattice models and energy functions
- **Quantum Algorithms Community** - For VQE implementations and optimizations
- **3Dmol.js Team** - For the molecular visualization library

## 📞 Support & Troubleshooting

**Common Issues:**
- **Memory errors**: Use shorter sequences (≤10 residues) or see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Slow convergence**: Try different optimizers or increase `max_iter`
- **Invalid structures**: Increase penalty weights in Hamiltonian
- **Web interface not loading**: Check Flask installation and port 5000 availability

**For help:**
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common solutions
2. Review example outputs in [`results/`](results/) directory
3. Verify all dependencies are installed: `pip install -r requirements.txt`
4. Ensure Python version ≥3.10
5. Open an issue on GitHub with error details

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐ on GitHub!

## 📊 Project Statistics

- **Lines of Code**: ~2,000+
- **Files**: 29
- **Languages**: Python, HTML, JavaScript, CSS
- **Dependencies**: 6 core packages
- **Documentation**: 1,500+ lines
- **Test Sequences**: 10+ examples

---

## 🎓 Educational Use

This project is perfect for:
- Learning quantum computing fundamentals
- Understanding VQE algorithm implementation
- Exploring protein folding biophysics
- Studying hybrid quantum-classical optimization
- Teaching computational biology concepts
- Demonstrating NISQ-era quantum applications

---

**⚠️ Disclaimer**: This is a research and educational tool. For production protein structure prediction in drug discovery or biotechnology, use established methods like AlphaFold, Rosetta, MODELLER, or I-TASSER.

---

**Built with ❤️ using Qiskit and Quantum Computing**

**Happy Quantum Computing! 🧬⚛️🚀**

---

## 📸 Screenshots

### Web Interface
![Main Interface](screenshots/main_interface.png)
*Upload sequences, configure options, and start predictions*

### 3D Interactive Viewer
![3D Viewer](screenshots/3d_viewer.png)
*360° rotation, multiple styles, and color schemes*

### Results Dashboard
![Results](screenshots/results.png)
*Download PDB files, images, and reports*

---

*Last Updated: November 2025*
