#!/usr/bin/env python3
"""
Demo script for Quantum Protein Structure Predictor
Showcases various features and use cases
"""

from quantum_protein_predictor import QuantumProteinPredictor

def demo_basic():
    """Basic single sequence prediction"""
    print("\n" + "="*70)
    print("DEMO 1: Basic Single Sequence Prediction")
    print("="*70)
    
    predictor = QuantumProteinPredictor()
    result = predictor.predict_structure(
        sequence="GYL",
        output_dir="demo_results"
    )
    
    if result:
        print(f"\n✅ Prediction successful!")
        print(f"Energy: {result['energy']:.6f}")
        print(f"Valid structure: {result['valid_structure']}")

def demo_advanced():
    """Advanced settings with custom parameters"""
    print("\n" + "="*70)
    print("DEMO 2: Advanced Configuration")
    print("="*70)
    
    predictor = QuantumProteinPredictor()
    result = predictor.predict_structure(
        sequence="ACDE",
        ansatz_type="twolocal",      # Different ansatz
        optimizer="SPSA",             # Different optimizer
        max_iter=100,                 # More iterations
        reps=3,                       # Deeper circuit
        output_dir="demo_results"
    )
    
    if result:
        print(f"\n✅ Advanced prediction complete!")
        print(f"Used {result['qubits']} qubits")
        print(f"Converged in {result['iterations']} iterations")

def demo_batch():
    """Batch processing multiple sequences"""
    print("\n" + "="*70)
    print("DEMO 3: Batch Processing")
    print("="*70)
    
    sequences = ["GY", "ACE", "FGH"]
    
    predictor = QuantumProteinPredictor()
    results = predictor.batch_predict(
        sequences,
        max_iter=30,  # Faster for demo
        output_dir="demo_results"
    )
    
    print("\n" + "="*70)
    print("BATCH RESULTS SUMMARY")
    print("="*70)
    for seq, result in results.items():
        if result:
            print(f"{seq}: Energy = {result['energy']:.4f}, "
                  f"Valid = {result['valid_structure']}, "
                  f"Rg = {result['radius_of_gyration']:.2f} Å")
        else:
            print(f"{seq}: FAILED")

def demo_comparison():
    """Compare different ansatz types"""
    print("\n" + "="*70)
    print("DEMO 4: Ansatz Comparison")
    print("="*70)
    
    sequence = "ACDE"
    ansatz_types = ["efficient_su2", "twolocal", "custom"]
    
    predictor = QuantumProteinPredictor()
    results = {}
    
    for ansatz in ansatz_types:
        print(f"\nTesting {ansatz}...")
        result = predictor.predict_structure(
            sequence=sequence,
            ansatz_type=ansatz,
            max_iter=30,
            output_dir="demo_results"
        )
        if result:
            results[ansatz] = result
    
    print("\n" + "="*70)
    print("ANSATZ COMPARISON RESULTS")
    print("="*70)
    for ansatz, result in results.items():
        print(f"{ansatz:15s}: Energy = {result['energy']:8.4f}, "
              f"Iterations = {result['iterations']:3d}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧬 QUANTUM PROTEIN STRUCTURE PREDICTOR - DEMO SUITE")
    print("="*70)
    print("\nThis demo will showcase various features:")
    print("1. Basic prediction")
    print("2. Advanced configuration")
    print("3. Batch processing")
    print("4. Ansatz comparison")
    print("\nNote: Each demo will take 30-60 seconds")
    
    input("\nPress Enter to start...")
    
    try:
        # Run demos
        demo_basic()
        demo_advanced()
        demo_batch()
        demo_comparison()
        
        print("\n" + "="*70)
        print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nCheck 'demo_results/' directory for output files")
        print("Each sequence has:")
        print("  - PDB structure file")
        print("  - 3D visualization")
        print("  - Convergence plot")
        print("  - JSON report")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
