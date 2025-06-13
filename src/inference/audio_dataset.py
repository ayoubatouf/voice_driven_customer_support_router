import os
from typing import List, Optional, Dict
import torch
import torchaudio
from torch.utils.data import Dataset


class CustomDataset(Dataset):
    def __init__(
        self,
        audio_files: List[str],
        basedir: Optional[str] = None,
        sampling_rate: int = 16000,
        max_audio_len_sec: float = 5.0,
    ):
        self.audio_files = audio_files
        self.basedir = basedir
        self.sampling_rate = sampling_rate
        self.max_len_samples = int(max_audio_len_sec * sampling_rate)

    def __len__(self) -> int:
        return len(self.audio_files)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        filepath = self.audio_files[idx]
        if self.basedir:
            filepath = os.path.join(self.basedir, filepath)

        waveform, sr = torchaudio.load(filepath)

        if waveform.size(0) > 1:
            waveform = waveform.mean(dim=0, keepdim=True)

        if sr != self.sampling_rate:
            resampler = torchaudio.transforms.Resample(
                orig_freq=sr, new_freq=self.sampling_rate
            )
            waveform = resampler(waveform)

        if waveform.size(1) > self.max_len_samples:
            waveform = waveform[:, : self.max_len_samples]
        elif waveform.size(1) < self.max_len_samples:
            padding = self.max_len_samples - waveform.size(1)
            waveform = torch.nn.functional.pad(waveform, (0, padding))

        return {"input_values": waveform.squeeze(0)}
