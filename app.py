from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

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

HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Forensic Analyzer</title><style>*{margin:0;padding:0;box-sizing:border-box;}body{background:#0f172a;color:white;font-family:Arial,sans-serif;padding:16px;}.container{max-width:95%;margin:0 auto;}h1{font-size:24px;margin-bottom:8px;}.subtitle{color:#94a3b8;margin-bottom:16px;font-size:13px;}.panel{background:#1e293b;border:1px solid #334155;border-radius:8px;padding:16px;margin-bottom:16px;}label{display:block;color:#cbd5e1;font-weight:bold;margin-bottom:6px;font-size:12px;}input{padding:10px;background:#334155;color:white;border:1px solid #475569;border-radius:6px;width:100%;font-size:13px;margin-bottom:8px;}input:focus{outline:none;border-color:#3b82f6;}button{padding:12px;background:#2563eb;color:white;border:none;border-radius:6px;cursor:pointer;font-weight:bold;font-size:13px;width:100%;margin-bottom:8px;}button:hover:not(:disabled){background:#1d4ed8;}button:disabled{opacity:0.5;cursor:not-allowed;}.tabs{display:flex;gap:10px;margin-bottom:16px;border-bottom:1px solid #334155;}.tab{padding:10px;cursor:pointer;color:#94a3b8;border:none;background:none;font-weight:bold;font-size:12px;}.tab.active{color:#60a5fa;border-bottom:2px solid #60a5fa;}.content{display:none;}.content.active{display:block;}.file-box{border:2px dashed #475569;border-radius:8px;padding:20px;text-align:center;}.file-icon{font-size:32px;margin-bottom:10px;}.step{background:#334155;padding:10px;margin-bottom:8px;border-radius:6px;display:flex;align-items:center;gap:8px;font-size:12px;}.step-icon{font-size:16px;min-width:20px;}.step.active{background:#1e3a8a;}.step.complete{background:#064e3b;}.error{background:#7f1d1d;border:1px solid #dc2626;color:#fca5a5;padding:10px;border-radius:6px;display:none;margin-bottom:12px;font-size:12px;}.file-info{background:#0f172a;border:1px solid #334155;padding:10px;border-radius:6px;margin-top:10px;display:none;font-size:11px;}.file-info.show{display:block;}.progress{display:none;background:#1e293b;border:1px solid #334155;padding:12px;border-radius:6px;margin-bottom:16px;}.progress.show{display:block;}.progress-bar{width:100%;height:22px;background:#0f172a;border:1px solid #334155;border-radius:4px;overflow:hidden;margin:6px 0;}.progress-fill{height:100%;background:linear-gradient(90deg,#3b82f6,#60a5fa);width:0%;transition:width 0.3s;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:bold;}.result-section{background:#1e293b;border:1px solid #334155;padding:12px;border-radius:6px;margin-bottom:12px;display:none;}.result-section.show{display:block;}.result-title{font-weight:bold;margin-bottom:8px;font-size:12px;}.result-content{background:#0f172a;padding:8px;border-radius:4px;max-height:250px;overflow-y:auto;font-size:11px;line-height:1.3;white-space:pre-wrap;word-wrap:break-word;}.success-btn{background:#16a34a;padding:14px;font-size:14px;margin-top:16px;}.success-btn:hover:not(:disabled){background:#15803d;}.export-btn{background:#16a34a;padding:8px;font-size:11px;width:auto;margin:0;}.complete{background:rgba(22,163,74,0.2);border:1px solid #22c55e;color:#86efac;padding:10px;border-radius:6px;display:none;font-size:12px;}.complete.show{display:block;}</style></head><body><div class="container"><h1>Forensic Analyzer</h1><p class="subtitle">Transcription → Analysis → Expert Report</p><div class="panel"><label>Deepgram API Key</label><input type="password" id="apiKey" placeholder="Your Deepgram key"><button type="button" onclick="toggleKey()" style="padding:8px;font-size:12px;">Show/Hide Key</button></div><div id="error" class="error"></div><div id="progress" class="progress"><div style="display:flex;justify-content:space-between;font-size:11px;color:#94a3b8;"><span id="progressLabel">Processing...</span><span id="progressPercent">0%</span></div><div class="progress-bar"><div id="progressFill" class="progress-fill"></div></div><div id="statusText" style="font-size:11px;color:#cbd5e1;margin-top:4px;">Starting...</div></div><div class="tabs"><button class="tab active" type="button" onclick="switchTab('upload')">Upload</button><button class="tab" id="resultTab" type="button" onclick="switchTab('results')" disabled>Results</button></div><div id="upload" class="content active"><div class="file-box"><div class="file-icon">📁</div><input type="file" id="fileInput" accept="audio/*,video/*"><div id="fileInfo" class="file-info"><p style="color:#4ade80;margin:0;">✓ <span id="fileName"></span></p><p style="color:#64748b;margin:4px 0 0 0;"><span id="fileSize"></span> MB</p></div></div><div class="panel" style="margin-top:16px;"><div style="font-weight:bold;margin-bottom:10px;font-size:12px;">Pipeline</div><div class="step" id="step1"><span class="step-icon">◯</span> 1. Transcription</div><div class="step" id="step2"><span class="step-icon">◯</span> 2. Analysis</div><div class="step" id="step3"><span class="step-icon">◯</span> 3. Report</div></div><button class="success-btn" id="startBtn" type="button" onclick="startAnalysis()">START ANALYSIS</button></div><div id="results" class="content"><div id="transcriptSection" class="result-section"><div class="result-title">Transcript</div><div class="result-content" id="transcript"></div></div><div id="analysisSection" class="result-section"><div class="result-title">Behavioral Analysis</div><div class="result-content" id="analysis"></div></div><div id="reportSection" class="result-section"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;"><div class="result-title" style="margin:0;">Expert Report</div><button class="export-btn" type="button" onclick="downloadReport()">⬇️ Export</button></div><div class="result-content" id="report"></div></div><div id="complete" class="complete"><div style="font-weight:bold;color:#86efac;font-size:13px;">✓ Complete</div><p style="font-size:11px;margin-top:4px;">Expert report ready. Export above.</p></div></div></div></body></html><script>let file=null;let data={};document.getElementById('fileInput').addEventListener('change',e=>{file=e.target.files[0];if(file){document.getElementById('fileName').textContent=file.name;document.getElementById('fileSize').textContent=(file.size/1024/1024).toFixed(1);document.getElementById('fileInfo').classList.add('show');hideError();}});function toggleKey(){const input=document.getElementById('apiKey');input.type=input.type==='password'?'text':'password';}function switchTab(tab){document.querySelectorAll('.content').forEach(el=>el.classList.remove('active'));document.querySelectorAll('.tab').forEach(el=>el.classList.remove('active'));document.getElementById(tab).classList.add('active');event.target.classList.add('active');}function showError(msg){document.getElementById('error').textContent=msg;document.getElementById('error').style.display='block';}function hideError(){document.getElementById('error').style.display='none';}function updateProgress(pct,label,status){const fill=document.getElementById('progressFill');fill.style.width=pct+'%';fill.textContent=pct+'%';document.getElementById('progressPercent').textContent=pct+'%';document.getElementById('progressLabel').textContent=label;document.getElementById('statusText').textContent=status;}function setStep(n,status){const el=document.getElementById('step'+n);el.classList.remove('active','complete');const icon=el.querySelector('.step-icon');if(status==='active'){el.classList.add('active');icon.textContent='⏳';}else if(status==='complete'){el.classList.add('complete');icon.textContent='✓';}else{icon.textContent='◯';}}async function startAnalysis(){if(!file){showError('Select file first');return;}if(!document.getElementById('apiKey').value){showError('Enter API key');return;}document.getElementById('startBtn').disabled=true;hideError();document.getElementById('progress').classList.add('show');try{setStep(1,'active');updateProgress(10,'Transcription','Uploading file...');const fd=new FormData();fd.append('file',file);fd.append('deepgram_key',document.getElementById('apiKey').value);updateProgress(20,'Transcription','Processing...');const res1=await fetch('/api/transcribe',{method:'POST',body:fd});if(!res1.ok){const err=await res1.json();throw new Error(err.error||'Transcription failed');}const d1=await res1.json();const transcript=d1.transcript;document.getElementById('transcript').textContent=transcript;document.getElementById('transcriptSection').classList.add('show');updateProgress(33,'Transcription','Done ✓');setStep(1,'complete');setStep(2,'active');updateProgress(40,'Analysis','Sending to Claude...');const res2=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({transcript})});if(!res2.ok){const err=await res2.json();throw new Error(err.error||'Analysis failed');}updateProgress(60,'Analysis','Processing...');const d2=await res2.json();const analysis=d2.analysis;document.getElementById('analysis').textContent=analysis;document.getElementById('analysisSection').classList.add('show');updateProgress(66,'Analysis','Done ✓');setStep(2,'complete');setStep(3,'active');updateProgress(70,'Report','Generating...');const res3=await fetch('/api/report',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({analysis})});if(!res3.ok){const err=await res3.json();throw new Error(err.error||'Report failed');}updateProgress(85,'Report','Finalizing...');const d3=await res3.json();const report=d3.report;document.getElementById('report').textContent=report;document.getElementById('reportSection').classList.add('show');document.getElementById('complete').classList.add('show');updateProgress(100,'Complete','All done ✓');setStep(3,'complete');data={transcript,analysis,report};document.getElementById('upload').classList.remove('active');document.getElementById('results').classList.add('active');document.querySelectorAll('.tab')[0].classList.remove('active');document.querySelectorAll('.tab')[1].classList.add('active');document.getElementById('resultTab').disabled=false;}catch(e){showError(e.message);document.getElementById('startBtn').disabled=false;}document.getElementById('progress').classList.remove('show');}function downloadReport(){const txt=`FORENSIC BEHAVIORAL ANALYSIS REPORT\n${new Date()}\n\n=== TRANSCRIPT ===\n${data.transcript}\n\n=== BEHAVIORAL ANALYSIS ===\n${data.analysis}\n\n=== LITIGATION-READY EXPERT REPORT ===\n${data.report}`;const blob=new Blob([txt]);const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='forensic-'+Date.now()+'.txt';a.click();}</script>"""

@app.route('/')
def index():
    return HTML

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
    app.run(host='0.0.0.0', port=int
