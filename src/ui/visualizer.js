class AudioVisualizer {
    constructor(visualizerElement, soundWaveElement) {
        this.visualizer = visualizerElement;
        this.soundWave = soundWaveElement;
        this.bars = [];
        this.setupBars();
    }

    setupBars() {
        for (let i = 0; i < 32; i++) {
            const bar = document.createElement('div');
            bar.classList.add('bar');
            bar.style.height = '5px';
            this.visualizer.appendChild(bar);
            this.bars.push(bar);
        }
    }

    start(analyser) {
        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        const animate = () => {
            if (!this.isActive) return;

            analyser.getByteFrequencyData(dataArray);
            const volume = this.getVolume(dataArray);
            const scale = 1 + (volume / 50);
            
            this.soundWave.style.transform = `scale(${scale})`;
            
            for (let i = 0; i < this.bars.length; i++) {
                const value = dataArray[i * 2] || 0;
                const height = Math.max(5, value / 255 * 100);
                this.bars[i].style.height = `${height}px`;
            }
            
            this.animationId = requestAnimationFrame(animate);
        };

        this.isActive = true;
        animate();
    }

    stop() {
        this.isActive = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        this.reset();
    }

    reset() {
        this.bars.forEach(bar => bar.style.height = '5px');
        this.soundWave.style.transform = 'scale(1)';
    }

    getVolume(dataArray) {
        return dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
    }
}

window.AudioVisualizer = AudioVisualizer;
