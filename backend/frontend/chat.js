// frontend/chat.js
class CureVoxUI {
  constructor() {
    this.chatWindow = document.getElementById('chatWindow');
    this.chatForm = document.getElementById('chatForm');
    this.symptomInput = document.getElementById('symptomInput');
    this.langInput = document.getElementById('langInput');
    this.startRecBtn = document.getElementById('startRecBtn');
    this.stopRecBtn = document.getElementById('stopRecBtn');
    this.audioPlayback = document.getElementById('audioPlayback');
    this.resultDiv = document.getElementById('result');
    this.rashInput = document.getElementById('rashInput');
    this.rashResult = document.getElementById('rashResult');
    this.spectrogramCanvas = document.getElementById('spectrogram');

    this.backendBase = 'http://127.0.0.1:5001';
    this.recChunks = [];
    this.mediaRecorder = null;
    this.audioCtx = null;
    this.analyser = null;
    this.dataArray = null;

    this.init();
  }

  init() {
    if (!this.chatForm) return;
    this.chatForm.addEventListener('submit', (e) => this.handleChat(e));
    if (this.startRecBtn) this.startRecBtn.onclick = () => this.startRecording();
    if (this.stopRecBtn) this.stopRecBtn.onclick = () => this.stopRecording();
    if (document.getElementById('uploadRashBtn')) {
      document.getElementById('uploadRashBtn').onclick = () => this.analyzeRash();
    }
    this.addMessage('👋 Hello — describe your symptoms, record a cough, or upload a rash photo.', 'AI');
    this.setupCanvas();
  }

  setupCanvas() {
    if (!this.spectrogramCanvas) return;
    this.spectrogramCanvas.width = this.spectrogramCanvas.offsetWidth * devicePixelRatio;
    this.spectrogramCanvas.height = this.spectrogramCanvas.offsetHeight * devicePixelRatio;
    this.spectrogramCtx = this.spectrogramCanvas.getContext('2d');
    this.spectrogramCtx.scale(devicePixelRatio, devicePixelRatio);
    window.addEventListener('resize', () => {
      this.spectrogramCanvas.width = this.spectrogramCanvas.offsetWidth * devicePixelRatio;
      this.spectrogramCanvas.height = this.spectrogramCanvas.offsetHeight * devicePixelRatio;
      this.spectrogramCtx.scale(devicePixelRatio, devicePixelRatio);
    });
  }

  addMessage(text, sender='AI') {
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble ' + (sender === 'AI' ? 'ai-bubble' : 'user-bubble');
    if (sender === 'AI') {
      const img = document.createElement('img');
      img.src = 'https://img.icons8.com/bubbles/100/robot-2.png';
      img.className = 'bubble-avatar';
      bubble.appendChild(img);
    }
    const content = document.createElement('div');
    content.className = 'bubble-content';
    content.innerHTML = text.replace(/\n/g, '<br>');
    bubble.appendChild(content);
    this.chatWindow.appendChild(bubble);
    this.chatWindow.scrollTop = this.chatWindow.scrollHeight;
  }

  async handleChat(e) {
    e.preventDefault();
    const msg = this.symptomInput.value.trim();
    if (!msg) return;
    this.addMessage(msg, 'User');
    this.symptomInput.value = '';
    this.addMessage('🔍 CureVox is thinking...', 'AI');

    try {
      const res = await fetch(`${this.backendBase}/predict`, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({symptoms: msg, lang: this.langInput.value})
      });
      const j = await res.json();
      this.chatWindow.lastElementChild.remove();
      if (j.ok) {
        const adv = j.payload.advice;
        const conf = Math.round((j.payload.confidence||0)*100);
        this.addMessage(`${adv}<br><small>Confidence: ${conf}%</small>`, 'AI');
        if ('speechSynthesis' in window) {
          const u = new SpeechSynthesisUtterance(adv);
          u.lang = this.langInput.value + '-IN';
          window.speechSynthesis.speak(u);
        }
      } else {
        this.addMessage('Error: ' + (j.message || 'prediction failed'), 'AI');
      }
    } catch (e) {
      this.chatWindow.lastElementChild.remove();
      this.addMessage('❌ Backend unreachable. Is the API running on port 5001?', 'AI');
    }
  }

  async startRecording() {
    this.startRecBtn.disabled = true;
    this.stopRecBtn.disabled = false;
    this.resultDiv.textContent = '🔴 Live spectrogram — cough now';
    try {
      const stream = await navigator.mediaDevices.getUserMedia({audio:true});
      this.mediaRecorder = new MediaRecorder(stream);
      this.recChunks = [];
      this.mediaRecorder.ondataavailable = e => this.recChunks.push(e.data);
      this.mediaRecorder.start();

      this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const src = this.audioCtx.createMediaStreamSource(stream);
      this.analyser = this.audioCtx.createAnalyser();
      this.analyser.fftSize = 2048;
      src.connect(this.analyser);
      this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
      this.drawSpectrogram();
    } catch (e) {
      this.resultDiv.textContent = '❌ Microphone error or denied';
      this.resetRecordingButtons();
    }
  }

  drawSpectrogram() {
    if (!this.analyser) return;
    this.analyser.getByteFrequencyData(this.dataArray);
    const ctx = this.spectrogramCtx;
    const width = this.spectrogramCanvas.width / devicePixelRatio;
    const height = this.spectrogramCanvas.height / devicePixelRatio;
    ctx.clearRect(0,0,width,height);
    const barW = width / this.dataArray.length;
    for (let i=0;i<this.dataArray.length;i++){
      const v = this.dataArray[i]/255;
      const h = v * height;
      const hue = Math.round((i/this.dataArray.length)*360);
      ctx.fillStyle = `hsl(${hue},100%,${30 + v*40}%)`;
      ctx.fillRect(i*barW, height-h, barW, h);
    }
    requestAnimationFrame(()=>this.drawSpectrogram());
  }

  async stopRecording() {
    this.stopRecBtn.disabled = true;
    this.startRecBtn.disabled = false;
    this.resultDiv.textContent = '⏳ Analyzing...';
    try {
      this.mediaRecorder.stop();
      // allow chunk collection
      await new Promise(r=>setTimeout(r, 300));
      const blob = new Blob(this.recChunks, {type:'audio/webm'});
      this.audioPlayback.src = URL.createObjectURL(blob);
      this.audioPlayback.style.display = '';
      const fd = new FormData();
      fd.append('audio', blob, 'cough.webm');
      const res = await fetch(`${this.backendBase}/analyze_audio`, {method:'POST', body: fd});
      const j = await res.json();
      if (j.ok) {
        const p = j.payload;
        this.resultDiv.innerHTML = `<strong>${p.label}</strong> — ${p.summary} <br>Confidence: ${Math.round((p.confidence||0)*100)}%`;
        this.addMessage(`Audio: ${p.summary} (Confidence ${Math.round((p.confidence||0)*100)}%)`, 'AI');
      } else {
        this.resultDiv.textContent = 'Analysis failed';
      }
    } catch (e) {
      this.resultDiv.textContent = 'Error analyzing audio';
    } finally {
      this.resetRecordingButtons();
    }
  }

  resetRecordingButtons() {
    if (this.startRecBtn) this.startRecBtn.disabled = false;
    if (this.stopRecBtn) this.stopRecBtn.disabled = true;
  }

  async analyzeRash() {
    if (!this.rashInput || !this.rashInput.files.length) {
      this.rashResult.textContent = 'Please select an image first.';
      return;
    }
    const file = this.rashInput.files[0];
    this.rashResult.textContent = '🔍 Analyzing...';
    const fd = new FormData();
    fd.append('image', file, file.name);
    try {
      const res = await fetch(`${this.backendBase}/analyze_rash`, {method:'POST', body: fd});
      const j = await res.json();
      if (j.ok) {
        const p = j.payload;
        this.rashResult.innerHTML = `<strong>${p.label}</strong> — ${p.summary}<br>Confidence: ${Math.round((p.confidence||0)*100)}%`;
        this.addMessage(`Rash: ${p.summary} (Confidence ${Math.round((p.confidence||0)*100)}%)`, 'AI');
      } else {
        this.rashResult.textContent = 'Analysis failed';
      }
    } catch (e) {
      this.rashResult.textContent = 'Error contacting backend';
    }
  }
}

document.addEventListener('DOMContentLoaded', () => new CureVoxUI());
