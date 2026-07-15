"""Redscape Archive Interface - Memento Edition"""
from flask import Flask, render_template, jsonify, request, send_from_directory
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
DATA_DIR = Path.home() / ".redscape" / "data"

# Register identity blueprint
from redscape.interface.identity import identity_bp
app.register_blueprint(identity_bp)

@app.route('/')
def index():
    """Main archive view"""
    return render_template('index.html')

@app.route('/api/cases')
def list_cases():
    """Return all scraped cases"""
    cases = []
    screenshots_dir = DATA_DIR / "screenshots"
    
    if screenshots_dir.exists():
        for case_dir in screenshots_dir.iterdir():
            if case_dir.is_dir():
                case_id = case_dir.name
                meta_file = case_dir / "meta.json"
                if meta_file.exists():
                    with open(meta_file) as f:
                        meta = json.load(f)
                else:
                    meta = {
                        'case_id': case_id,
                        'target': 'Unknown',
                        'timestamp': 'Unknown',
                        'pages': 0
                    }
                cases.append(meta)
    
    return jsonify(sorted(cases, key=lambda x: x.get('timestamp', ''), reverse=True))

@app.route('/api/case/<case_id>')
def get_case(case_id):
    """Return specific case details"""
    case_dir = DATA_DIR / "screenshots" / case_id
    if not case_dir.exists():
        return jsonify({'error': 'Case not found'}), 404
    
    meta_file = case_dir / "meta.json"
    if meta_file.exists():
        with open(meta_file) as f:
            data = json.load(f)
    else:
        data = {'case_id': case_id, 'pages': []}
    
    screenshots = []
    for img in case_dir.glob("*.png"):
        screenshots.append(img.name)
    
    data['screenshots'] = screenshots
    return jsonify(data)

@app.route('/api/screenshot/<case_id>/<filename>')
def serve_screenshot(case_id, filename):
    """Serve screenshot image"""
    case_dir = DATA_DIR / "screenshots" / case_id
    return send_from_directory(case_dir, filename)

def start_interface(host='127.0.0.1', port=5000, debug=False):
    """Start the archive interface"""
    print(f"[+] Redscape Archive starting at http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    start_interface(debug=True)