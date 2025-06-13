# LibriClean 100 Dataset

## Dataset Overview

The `LibriClean` 100 dataset is a subset of the LibriSpeech corpus consisting of approximately 100 hours of clean, read English speech sampled at 16 kHz. The audio is derived from public domain audiobooks from the LibriVox project, carefully segmented and aligned.

- Sampling Rate: 16,000 Hz

- Format: Parquet files containing audio and transcription data

- Total Size: ~6.4 GB

- Number of Examples:

        Train: 28,539

        Test: 2,620

The dataset is widely used for ASR model training and benchmarking.

## Citation
```
@inproceedings{panayotov2015librispeech,
  title={Librispeech: an ASR corpus based on public domain audio books},
  author={Panayotov, Vassil and Chen, Guoguo and Povey, Daniel and Khudanpur, Sanjeev},
  booktitle={Acoustics, Speech and Signal Processing (ICASSP), 2015 IEEE International Conference on},
  pages={5206--5210},
  year={2015},
  organization={IEEE}
}
```
## Download and Installation
Clone this repository to download the dataset files:

```
git clone https://huggingface.co/datasets/nguyenvulebinh/libris_clean_100

```

## Dataset Features
Each example contains the following fields:

| Feature      | Type   | Description                            |
| ------------ | ------ | ------------------------------------ |
| `file`       | string | file path or identifier for the audio|
| `audio`      | Audio  | audio waveform, 16kHz, mono          |
| `text`       | string | corresponding transcription text     |
| `speaker_id` | int64  | identifier of the speaker             |
| `chapter_id` | int64  | identifier of the audiobook chapter  |
| `id`         | string | unique identifier for the audio sample|


