from flask import Flask, render_template, request, jsonify
import requests
import os
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

DECEPTION_PATTERNS = """CLETO DECEPTION PATTERNS (July 18, 2025):
1. Timeline Fabrication: Calls police AFTER deploying pepper spray
2. Contact Point Shifting: Shoulder → Arm (narrative reconstruction)
3. Narrative Framing: Pre-emptive "Criminal Trespass" positioning
4. Character Bolstering: Authority/compassion emphasis
5. False Witness Invention: Non-present corroborating witnesses
6. Reactive Pivoting: "Oh he called you?" → immediate narrative shift
7. Escalation Minimization: Admits sign-touching but reframes victim
8. Post-Incident Control: Updates record proactively for liability mitigation
9. Authority-Seeking Pattern: Quasi-law enforcement despite disqualifying background"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        deepgram_key = request.form.get('deepgram_key')
        
        if not deepgram_key:
            return jsonify({'error': 'No Deepgram key provided'}), 400

        headers = {'Authorization': f'Token {deepgram_key}'}
        files = {'file': (file.filename, file.stream, file.content_type)}
        
        response = requests.post(
            'https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true',
            headers=headers,
            files=files,
            timeout=300
        )
        
        if response.status_code != 200:
            return jsonify({'error': f'Deepgram error: {response.status_code}'}), 400
        
        data = response.json()
        transcript = data.get('results', {}).get('channels', [{}])[0].get('alternatives', [{}])[0].get('transcript', '')
        
        if not transcript:
            return jsonify({'error': 'No transcript returned'}), 400
        
        return jsonify({'transcript': transcript, 'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        transcript = data.get('transcript')
        
        if not transcript:
            return jsonify({'error': 'No transcript provided'}), 400

        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={'Content-Type': 'application/json'},
            json={
                'model': 'claude-sonnet-4-20250514',
                'max_tokens': 3000,
                'messages': [{
                    'role': 'user',
                    'content': f"""Expert forensic behavioral analyst. Known deception patterns:
{DECEPTION_PATTERNS}

Analyze this transcript for: 1) Deception indicators 2) Timeline issues 3) Narrative shifts 4) Contact point inconsistencies 5) Character bolstering 6) False witnesses 7) Defensive pivoting 8) Pattern matching 9) Credibility rating (1-10).

TRANSCRIPT:
{transcript}

Format for expert witness testimony with specific citations."""
                }]
            },
            timeout=60
        )
        
        if response.status_code != 200:
            return jsonify({'error': f'Claude error: {response.status_code}'}), 400
        
        analysis = response.json()['content'][0]['text']
        return jsonify({'analysis': analysis, 'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/report', methods=['POST'])
def generate_report():
    try:
        data = request.json
        analysis = data.get('analysis')
        
        if not analysis:
            return jsonify({'error': 'No analysis provided'}), 400

        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={'Content-Type': 'application/json'},
            json={
                'model': 'claude-sonnet-4-20250514',
                'max_tokens': 2500,
                'messages': [{
                    'role': 'user',
                    'content': f"""Create LITIGATION-READY EXPERT REPORT for deposition/trial testimony.

Format:
1) EXECUTIVE SUMMARY (100 words) - Overall credibility assessment
2) CRITICAL FINDINGS (3-5 bullets) - Specific deceptions and red flags
3) COMPARISON TO JULY 18 STATEMENTS - Inconsistencies and pattern evolution
4) CREDIBILITY RATING - Score with reasoning
5) EXPERT CONCLUSION - Statement suitable for under-oath testimony

ANALYSIS:
{analysis}"""
                }]
            },
            timeout=60
        )
        
        if response.status_code != 200:
            return jsonify({'error': f'Claude error: {response.status_code}'}), 400
        
        report = response.json()['content'][0]['text']
        return jsonify({'report': report, 'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
