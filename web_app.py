# Web Interface for Quantum Protein Structure Predictor
# A Flask-based web application with real-time visualization and interactive 3D viewing

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import os
import json
import time
from datetime import datetime
from werkzeug.utils import secure_filename
import threading
from quantum_protein_predictor import QuantumProteinPredictor

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'web_results'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.secret_key = 'quantum_protein_predictor_secret_key_2025'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
os.makedirs('static/results', exist_ok=True)

# Store active jobs
active_jobs = {}

@app.route('/')
def index():
    """Main page with upload interface"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction request"""
    try:
        data = request.get_json()
        sequence = data.get('sequence', '').strip().upper()
        ansatz = data.get('ansatz', 'efficient_su2')
        optimizer = data.get('optimizer', 'COBYLA')
        max_iter = int(data.get('max_iter', 50))
        reps = int(data.get('reps', 2))
        
        # Validate sequence
        from step1_validation import validate_sequence
        is_valid, msg = validate_sequence(sequence)
        
        if not is_valid:
            return jsonify({
                'success': False,
                'error': msg
            }), 400
        
        # Create job ID
        job_id = f"{sequence}_{int(time.time())}"
        
        # Start prediction in background
        def run_prediction():
            try:
                predictor = QuantumProteinPredictor()
                result = predictor.predict_structure(
                    sequence=sequence,
                    ansatz_type=ansatz,
                    optimizer=optimizer,
                    max_iter=max_iter,
                    reps=reps,
                    output_dir=os.path.join(app.config['RESULTS_FOLDER'], job_id)
                )
                
                if result:
                    active_jobs[job_id] = {
                        'status': 'completed',
                        'result': result,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    active_jobs[job_id] = {
                        'status': 'failed',
                        'error': 'Prediction failed',
                        'timestamp': datetime.now().isoformat()
                    }
            except Exception as e:
                active_jobs[job_id] = {
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        # Initialize job status
        active_jobs[job_id] = {
            'status': 'running',
            'sequence': sequence,
            'started': datetime.now().isoformat()
        }
        
        # Run in background thread
        thread = threading.Thread(target=run_prediction)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Prediction started'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/status/<job_id>')
def check_status(job_id):
    """Check job status"""
    if job_id not in active_jobs:
        return jsonify({
            'success': False,
            'error': 'Job not found'
        }), 404
    
    job_data = active_jobs[job_id]
    
    if job_data['status'] == 'completed':
        result = job_data['result']
        return jsonify({
            'success': True,
            'status': 'completed',
            'result': {
                'sequence': result['sequence'],
                'energy': result['energy'],
                'valid_structure': result['valid_structure'],
                'radius_of_gyration': result['radius_of_gyration'],
                'iterations': result['iterations'],
                'qubits': result['qubits'],
                'job_id': job_id
            }
        })
    elif job_data['status'] == 'failed':
        return jsonify({
            'success': False,
            'status': 'failed',
            'error': job_data.get('error', 'Unknown error')
        })
    else:
        return jsonify({
            'success': True,
            'status': 'running',
            'message': 'Prediction in progress...'
        })

@app.route('/download/<job_id>/<file_type>')
def download_file(job_id, file_type):
    """Download result files"""
    if job_id not in active_jobs or active_jobs[job_id]['status'] != 'completed':
        return "File not found", 404
    
    result = active_jobs[job_id]['result']
    sequence = result['sequence']
    job_dir = os.path.join(app.config['RESULTS_FOLDER'], job_id)
    
    file_map = {
        'pdb': f'{sequence}_structure.pdb',
        'image': f'{sequence}_structure_3d.png',
        'convergence': f'{sequence}_convergence.png',
        'report': f'{sequence}_report.json'
    }
    
    if file_type not in file_map:
        return "Invalid file type", 400
    
    file_path = os.path.join(job_dir, file_map[file_type])
    
    if not os.path.exists(file_path):
        return "File not found", 404
    
    return send_file(file_path, as_attachment=True)

@app.route('/viewer/<job_id>')
def viewer(job_id):
    """Interactive 3D viewer page"""
    if job_id not in active_jobs or active_jobs[job_id]['status'] != 'completed':
        return "Results not found", 404
    
    result = active_jobs[job_id]['result']
    return render_template('viewer.html', job_id=job_id, result=result)

@app.route('/pdb/<job_id>')
def get_pdb(job_id):
    """Get PDB file content for 3D viewer"""
    if job_id not in active_jobs or active_jobs[job_id]['status'] != 'completed':
        return "File not found", 404
    
    result = active_jobs[job_id]['result']
    sequence = result['sequence']
    job_dir = os.path.join(app.config['RESULTS_FOLDER'], job_id)
    pdb_file = os.path.join(job_dir, f'{sequence}_structure.pdb')
    
    if not os.path.exists(pdb_file):
        return "PDB file not found", 404
    
    with open(pdb_file, 'r') as f:
        pdb_content = f.read()
    
    return pdb_content, 200, {'Content-Type': 'text/plain'}

@app.route('/image/<job_id>/<image_type>')
def get_image(job_id, image_type):
    """Serve images"""
    if job_id not in active_jobs or active_jobs[job_id]['status'] != 'completed':
        return "Image not found", 404
    
    result = active_jobs[job_id]['result']
    sequence = result['sequence']
    job_dir = os.path.join(app.config['RESULTS_FOLDER'], job_id)
    
    if image_type == 'structure':
        image_file = f'{sequence}_structure_3d.png'
    elif image_type == 'convergence':
        image_file = f'{sequence}_convergence.png'
    else:
        return "Invalid image type", 400
    
    image_path = os.path.join(job_dir, image_file)
    
    if not os.path.exists(image_path):
        return "Image not found", 404
    
    return send_file(image_path, mimetype='image/png')

@app.route('/batch', methods=['POST'])
def batch_predict():
    """Handle batch predictions from file upload"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    # Read sequences from file
    try:
        content = file.read().decode('utf-8')
        sequences = [line.strip().upper() for line in content.split('\n') if line.strip()]
        
        if not sequences:
            return jsonify({'success': False, 'error': 'No sequences found in file'}), 400
        
        # Validate all sequences first
        invalid = []
        for seq in sequences:
            from step1_validation import validate_sequence
            is_valid, msg = validate_sequence(seq)
            if not is_valid:
                invalid.append(f"{seq}: {msg}")
        
        if invalid:
            return jsonify({
                'success': False,
                'error': 'Invalid sequences found',
                'details': invalid
            }), 400
        
        # Create batch job
        batch_id = f"batch_{int(time.time())}"
        job_ids = []
        
        for seq in sequences:
            job_id = f"{seq}_{int(time.time())}_{len(job_ids)}"
            job_ids.append(job_id)
            
            # Start each prediction
            def run_batch_prediction(sequence, jid):
                try:
                    predictor = QuantumProteinPredictor()
                    result = predictor.predict_structure(
                        sequence=sequence,
                        output_dir=os.path.join(app.config['RESULTS_FOLDER'], jid)
                    )
                    if result:
                        active_jobs[jid] = {'status': 'completed', 'result': result}
                    else:
                        active_jobs[jid] = {'status': 'failed', 'error': 'Prediction failed'}
                except Exception as e:
                    active_jobs[jid] = {'status': 'failed', 'error': str(e)}
            
            active_jobs[job_id] = {'status': 'running', 'sequence': seq}
            thread = threading.Thread(target=run_batch_prediction, args=(seq, job_id))
            thread.daemon = True
            thread.start()
            
            time.sleep(0.1)  # Small delay between starts
        
        return jsonify({
            'success': True,
            'batch_id': batch_id,
            'job_ids': job_ids,
            'count': len(sequences)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("="*70)
    print("🧬 QUANTUM PROTEIN STRUCTURE PREDICTOR - WEB INTERFACE")
    print("="*70)
    print("\n🌐 Starting web server...")
    print(f"📍 URL: http://localhost:5000")
    print("\n✨ Features:")
    print("   • Upload sequences via browser")
    print("   • Real-time prediction status")
    print("   • Interactive 3D visualization")
    print("   • Download PDB, images, reports")
    print("   • Batch processing from files")
    print("\n🚀 Press Ctrl+C to stop")
    print("="*70)
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
