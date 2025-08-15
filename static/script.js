// TTS Application JavaScript
class TTSApp {
    constructor() {
        this.currentAudio = null;
        this.isPlaying = false;
        this.isLoading = false;
        this.init();
    }

    init() {
        // Form submission handler
        document.getElementById('ttsForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateTTS();
        });

        console.log('🎤 TTS Generator Ready!');
    }

    async generateTTS() {
        if (this.isLoading) return;

        const text = document.getElementById('text').value.trim();
        const voiceId = document.getElementById('voice_id').value;
        const style = document.getElementById('style').value;

        if (!text) {
            this.showError('Please enter some text to convert to speech.');
            return;
        }

        this.setLoading(true);
        this.showResult('loading', 'Generating audio with Murf AI...', '');

        try {
            const response = await fetch('/tts/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    voice_id: voiceId,
                    style: style
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to generate audio');
            }

            if (data.success && data.audio_url) {
                this.showAudioPlayer(data, text);
            } else {
                throw new Error(data.message || 'No audio URL received');
            }

        } catch (error) {
            console.error('TTS Generation Error:', error);
            this.showError(`Failed to generate audio: ${error.message}`);
        } finally {
            this.setLoading(false);
        }
    }

    showAudioPlayer(data, originalText) {
        const wordCount = data.word_count || originalText.split(' ').length;
        const estimatedDuration = Math.ceil(wordCount * 0.5); // Rough estimate

        const audioPlayerHTML = `
            <div class="message success-message">
                ✅ Audio generated successfully!
            </div>
            <div class="audio-player-container">
                <div class="audio-info">
                    <h3>🎵 Generated Audio</h3>
                    <div class="audio-stats">
                        <span>📝 Words: ${wordCount}</span>
                        <span>⏱️ Est. Duration: ${estimatedDuration}s</span>
                    </div>
                </div>
                
                <div class="custom-audio-player">
                    <button class="play-pause-btn" id="playPauseBtn">
                        ▶️
                    </button>
                    
                    <div class="progress-container" id="progressContainer">
                        <div class="progress-bar" id="progressBar"></div>
                    </div>
                    
                    <div class="time-display" id="timeDisplay">
                        0:00 / 0:00
                    </div>
                    
                    <div class="volume-container">
                        <span>🔊</span>
                        <input type="range" class="volume-slider" id="volumeSlider" min="0" max="100" value="100">
                    </div>
                </div>
                
                <audio id="audioElement" preload="auto" style="display: none;">
                    <source src="${data.audio_url}" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>
            </div>
        `;

        this.showResult('success', '', audioPlayerHTML);
        this.initializeAudioPlayer();
    }

    initializeAudioPlayer() {
        this.currentAudio = document.getElementById('audioElement');
        const playPauseBtn = document.getElementById('playPauseBtn');
        const progressContainer = document.getElementById('progressContainer');
        const progressBar = document.getElementById('progressBar');
        const timeDisplay = document.getElementById('timeDisplay');
        const volumeSlider = document.getElementById('volumeSlider');

        // Play/Pause functionality
        playPauseBtn.addEventListener('click', () => {
            if (this.isPlaying) {
                this.pauseAudio();
            } else {
                this.playAudio();
            }
        });

        // Progress bar click to seek
        progressContainer.addEventListener('click', (e) => {
            const clickX = e.offsetX;
            const width = progressContainer.offsetWidth;
            const duration = this.currentAudio.duration;
            const newTime = (clickX / width) * duration;
            this.currentAudio.currentTime = newTime;
        });

        // Volume control
        volumeSlider.addEventListener('input', (e) => {
            this.currentAudio.volume = e.target.value / 100;
        });

        // Audio event listeners
        this.currentAudio.addEventListener('loadedmetadata', () => {
            this.updateTimeDisplay();
        });

        this.currentAudio.addEventListener('timeupdate', () => {
            this.updateProgress();
            this.updateTimeDisplay();
        });

        this.currentAudio.addEventListener('ended', () => {
            this.isPlaying = false;
            playPauseBtn.innerHTML = '▶️';
            progressBar.style.width = '0%';
        });

        this.currentAudio.addEventListener('error', (e) => {
            console.error('Audio loading error:', e);
            this.showError('Failed to load audio file. Please try generating again.');
        });

        // Auto-load audio
        this.currentAudio.load();
    }

    playAudio() {
        if (this.currentAudio) {
            this.currentAudio.play().then(() => {
                this.isPlaying = true;
                document.getElementById('playPauseBtn').innerHTML = '⏸️';
            }).catch((error) => {
                console.error('Play error:', error);
                this.showError('Failed to play audio. Please try again.');
            });
        }
    }

    pauseAudio() {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.isPlaying = false;
            document.getElementById('playPauseBtn').innerHTML = '▶️';
        }
    }

    updateProgress() {
        if (this.currentAudio && this.currentAudio.duration) {
            const progress = (this.currentAudio.currentTime / this.currentAudio.duration) * 100;
            document.getElementById('progressBar').style.width = progress + '%';
        }
    }

    updateTimeDisplay() {
        if (this.currentAudio) {
            const current = this.formatTime(this.currentAudio.currentTime || 0);
            const duration = this.formatTime(this.currentAudio.duration || 0);
            document.getElementById('timeDisplay').textContent = `${current} / ${duration}`;
        }
    }

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    showResult(type, message, content) {
        const resultSection = document.getElementById('resultSection');
        const resultContent = document.getElementById('resultContent');
        
        resultSection.className = `result-section ${type}`;
        resultSection.classList.remove('hidden');
        
        let html = '';
        if (message) {
            const messageClass = type === 'error' ? 'error-message' : 
                                type === 'loading' ? 'loading-message' : 'success-message';
            html += `<div class="message ${messageClass}">`;
            if (type === 'loading') {
                html += `<span class="loading-spinner"></span> `;
            }
            html += `${message}</div>`;
        }
        
        if (content) {
            html += content;
        }
        
        resultContent.innerHTML = html;
        
        // Scroll to result
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    showError(message) {
        this.showResult('error', `❌ ${message}`, '');
    }

    setLoading(loading) {
        this.isLoading = loading;
        const btn = document.getElementById('generateBtn');
        
        if (loading) {
            btn.disabled = true;
            btn.innerHTML = '<span class="loading-spinner"></span> Generating...';
        } else {
            btn.disabled = false;
            btn.innerHTML = '🎯 Generate Audio';
        }
    }
}

// Initialize the TTS app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TTSApp();
});

// Show welcome message
console.log('🚀 Welcome to 30 Days of MurfAI - Advanced TTS Generator!');
