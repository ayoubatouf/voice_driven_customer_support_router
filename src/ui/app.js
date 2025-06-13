document.addEventListener('DOMContentLoaded', () => {
    const listenBtn = document.getElementById('listenBtn');
    const statusText = document.getElementById('status');
    const soundWave = document.getElementById('soundWave');
    const timerElement = document.getElementById('timer');
    const visualizer = document.getElementById('visualizer');
    const resultDiv = document.getElementById('result');

    const audioVisualizer = new AudioVisualizer(visualizer, soundWave);
    let isRecording = false;
    let recorder;
    let audioStream;
    let audioContext;
    let timerInterval;
    let timeLeft = 10;

    function updateTimer(seconds) {
        timeLeft = seconds;
        const formattedTime = `00:${seconds.toString().padStart(2, '0')}`;
        timerElement.textContent = formattedTime;
    }

    function resetUI() {
        updateTimer(10);
        listenBtn.classList.remove('recording');
        statusText.innerHTML = '<i class="fas fa-info-circle"></i> Press the microphone button and speak to begin';
        audioVisualizer.reset();
    }

    listenBtn.onclick = async () => {
        if (isRecording) return;

        listenBtn.disabled = true;
        resetUI();

        try {
            audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            await audioContext.resume();

            const input = audioContext.createMediaStreamSource(audioStream);
            const analyser = audioContext.createAnalyser();
            analyser.fftSize = 1024;
            input.connect(analyser);

            recorder = new Recorder(input, { numChannels: 1 });

            function startRecording() {
                isRecording = true;
                listenBtn.classList.add('recording');
                statusText.innerHTML = '<i class="fas fa-circle"></i> Recording... Speak now';
                recorder.record();
                audioVisualizer.start(analyser);

                updateTimer(10);
                clearInterval(timerInterval);
                timerInterval = setInterval(() => {
                    timeLeft--;
                    updateTimer(timeLeft);

                    if (timeLeft <= 0) {
                        clearInterval(timerInterval);
                        stopRecording();
                    }
                }, 1000);
            }

            startRecording();

        } catch (err) {
            statusText.innerHTML = `<i class="fas fa-exclamation-circle"></i> Microphone access error: ${err.message}`;
            listenBtn.disabled = false;
        }
    };

    function stopRecording() {
        if (!isRecording) return;

        isRecording = false;
        recorder.stop();
        audioStream.getTracks().forEach(track => track.stop());
        audioVisualizer.stop();
        clearInterval(timerInterval);

        statusText.innerHTML = '<i class="fas fa-sync fa-spin"></i> Processing your request...';

        recorder.exportWAV(async (blob) => {
            const file = new File([blob], "audio.wav", { type: "audio/wav" });
            const formData = new FormData();
            formData.append("file", file);

            try {
                const response = await fetch("http://localhost:8000/route-customer-to-agent/", {
                    method: "POST",
                    body: formData
                });

                if (!response.ok) {
                    const error = await response.json();
                    resultDiv.innerHTML = `<div class="no-agent" style="color: #e74c3c;">
                        <i class="fas fa-exclamation-triangle"></i>
                        <h3>Error Processing Request</h3>
                        <p>${error.detail || 'Please try again'}</p>
                    </div>`;
                    statusText.innerHTML = '<i class="fas fa-times-circle"></i> Error processing request';
                    listenBtn.disabled = false;
                    return;
                }

                const data = await response.json();
                const agent = data.assigned_agent || {};

                const languages = typeof agent.languages === "string" ?
                    JSON.parse(agent.languages) : agent.languages || [];
                const skills = typeof agent.skills === "string" ?
                    JSON.parse(agent.skills) : agent.skills || [];

                let initials = "AG";
                if (agent.name) {
                    const nameParts = agent.name.split(' ');
                    if (nameParts.length > 1) {
                        initials = nameParts[0][0] + nameParts[1][0];
                    } else if (agent.name.length >= 2) {
                        initials = agent.name.substring(0, 2);
                    }
                }

                resultDiv.innerHTML = `
                    <div class="agent-card">
                        <div class="agent-header">
                            <div class="agent-avatar">${initials}</div>
                            <div class="agent-info">
                                <h3>${agent.name || "Agent Name"}</h3>
                                <div class="agent-id">${agent.agent_id || "AG-XXXX"}</div>
                            </div>
                        </div>
                        
                        <div class="agent-details">
                            <div class="detail-item">
                                <h4><i class="fas fa-venus-mars"></i> Gender</h4>
                                <p>${agent.gender || "N/A"}</p>
                            </div>
                            
                            <div class="detail-item">
                                <h4><i class="fas fa-language"></i> Languages</h4>
                                <div class="tags">
                                    ${languages.map(lang => `<span class="tag">${lang}</span>`).join('')}
                                    ${languages.length === 0 ? '<span class="tag">None</span>' : ''}
                                </div>
                            </div>
                            
                            <div class="detail-item">
                                <h4><i class="fas fa-star"></i> Experience</h4>
                                <p>${agent.experience || 0} years</p>
                            </div>
                            
                            <div class="detail-item">
                                <h4><i class="fas fa-tasks"></i> Current Load</h4>
                                <p>${agent.current_load ?? "N/A"}</p>
                            </div>
                            
                            <div class="detail-item">
                                <h4><i class="fas fa-briefcase"></i> Skills</h4>
                                <div class="tags">
                                    ${skills.map(skill => `<span class="tag">${skill}</span>`).join('')}
                                    ${skills.length === 0 ? '<span class="tag">None</span>' : ''}
                                </div>
                            </div>
                            
                            <div class="detail-item">
                                <h4><i class="fas fa-user-check"></i> Availability</h4>
                                <p style="color: ${agent.is_available ? '#27ae60' : '#e74c3c'}">
                                    ${agent.is_available ? "Available" : "Not Available"}
                                </p>
                            </div>
                        </div>
                    </div>
                `;

                statusText.innerHTML = '<i class="fas fa-check-circle"></i> Agent matched successfully!';
            } catch (err) {
                resultDiv.innerHTML = `<div class="no-agent" style="color: #e74c3c;">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Connection Error</h3>
                    <p>${err.message || 'Failed to connect to API'}</p>
                </div>`;
                statusText.innerHTML = '<i class="fas fa-times-circle"></i> Error connecting to API';
            } finally {
                listenBtn.disabled = false;
            }
        });
    }

    updateTimer(10);
    document.querySelector('header').style.animation = 'fadeIn 1s ease';
});
