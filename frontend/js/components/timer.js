/**
 * GoalMate Focus Timer Component
 * Supports Focus (45:00), Short Break (5:00), Long Break (15:00)
 * Uses SVG circular progress, audio chime synthesis via Web Audio API.
 */

const FocusTimer = {
    mode: 'focus', // 'focus', 'shortBreak', 'longBreak'
    durations: {
        focus: 45 * 60,
        shortBreak: 5 * 60,
        longBreak: 15 * 60
    },
    timeLeft: 45 * 60,
    isRunning: false,
    timerId: null,

    init() {
        this.timeLeft = this.durations[this.mode];
        this.render();
    },

    setMode(newMode) {
        if (this.isRunning) this.pause();
        this.mode = newMode;
        this.timeLeft = this.durations[newMode];
        this.render();
    },

    start() {
        if (this.isRunning) return;
        this.isRunning = true;
        this.timerId = setInterval(() => {
            if (this.timeLeft > 0) {
                this.timeLeft--;
                this.updateDisplay();
            } else {
                this.complete();
            }
        }, 1000);
        this.updateControls();
    },

    pause() {
        if (!this.isRunning) return;
        this.isRunning = false;
        clearInterval(this.timerId);
        this.timerId = null;
        this.updateControls();
    },

    reset() {
        this.pause();
        this.timeLeft = this.durations[this.mode];
        this.render();
    },

    complete() {
        this.pause();
        this.playChime();
        if (window.store) {
            const minutes = Math.round(this.durations[this.mode] / 60);
            window.store.logFocusSession(minutes, this.mode === 'focus' ? 'Focus' : 'Break');
        }
        alert(`🎉 Well done! You finished your ${this.mode === 'focus' ? '45-minute Focus' : 'Break'} session!`);
        this.reset();
    },

    playChime() {
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.type = 'sine';
            osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
            osc.frequency.setValueAtTime(880, ctx.currentTime + 0.15); // A5
            gain.gain.setValueAtTime(0.3, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.8);
            osc.start(ctx.currentTime);
            osc.stop(ctx.currentTime + 0.8);
        } catch (e) {
            console.log("Audio play error:", e);
        }
    },

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    },

    render() {
        const container = document.getElementById('focus-timer-widget');
        if (!container) return;

        const total = this.durations[this.mode];
        const progress = (total - this.timeLeft) / total;
        const circumference = 2 * Math.PI * 52; // r = 52
        const strokeDashoffset = circumference * (1 - progress);

        container.innerHTML = `
            <div class="card timer-card">
                <div class="card-header">
                    <span class="card-title"><span class="icon">⏱️</span> Focus Timer</span>
                </div>
                
                <div class="timer-mode-selector">
                    <button class="timer-mode-btn ${this.mode === 'focus' ? 'active' : ''}" onclick="FocusTimer.setMode('focus')">Focus</button>
                    <button class="timer-mode-btn ${this.mode === 'shortBreak' ? 'active' : ''}" onclick="FocusTimer.setMode('shortBreak')">Short Break</button>
                    <button class="timer-mode-btn ${this.mode === 'longBreak' ? 'active' : ''}" onclick="FocusTimer.setMode('longBreak')">Long Break</button>
                </div>

                <div class="timer-dial-wrapper">
                    <svg class="timer-svg" width="130" height="130" viewBox="0 0 130 130">
                        <circle class="timer-circle-bg" cx="65" cy="65" r="52"></circle>
                        <circle id="timer-circle-progress" class="timer-circle-fg" cx="65" cy="65" r="52" 
                            style="stroke-dasharray: ${circumference}; stroke-dashoffset: ${strokeDashoffset};"></circle>
                    </svg>
                    <div class="timer-display-inner">
                        <span id="timer-time-text" class="timer-digits">${this.formatTime(this.timeLeft)}</span>
                        <div class="timer-play-btn-wrap">
                            <button id="timer-toggle-btn" class="timer-action-play" onclick="FocusTimer.toggle()">
                                ${this.isRunning ? '⏸️' : '▶️'}
                            </button>
                        </div>
                    </div>
                </div>

                <div class="timer-bottom-controls">
                    <button class="btn btn-xs btn-outline" onclick="FocusTimer.reset()">Reset</button>
                </div>

                <p class="timer-quote">"Discipline is just love for your future self."</p>
            </div>
        `;
    },

    toggle() {
        if (this.isRunning) {
            this.pause();
        } else {
            this.start();
        }
    },

    updateDisplay() {
        const textEl = document.getElementById('timer-time-text');
        const circleEl = document.getElementById('timer-circle-progress');
        if (textEl) textEl.textContent = this.formatTime(this.timeLeft);

        if (circleEl) {
            const total = this.durations[this.mode];
            const progress = (total - this.timeLeft) / total;
            const circumference = 2 * Math.PI * 52;
            const offset = circumference * (1 - progress);
            circleEl.style.strokeDashoffset = offset;
        }
    },

    updateControls() {
        const toggleBtn = document.getElementById('timer-toggle-btn');
        if (toggleBtn) {
            toggleBtn.innerHTML = this.isRunning ? '⏸️' : '▶️';
            toggleBtn.classList.toggle('playing', this.isRunning);
        }
    }
};

window.FocusTimer = FocusTimer;
