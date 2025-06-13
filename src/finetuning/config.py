from dataclasses import dataclass


@dataclass
class Config:
    base_path: str = "../data/libris_clean_100/data"
    checkpoint: str = "facebook/wav2vec2-xls-r-300m"
    sampling_rate: int = 16000
    num_labels: int = 2
    output_dir: str = "./wav2vec2-finetuned"
    batch_size: int = 8
    num_epochs: int = 1
    learning_rate: float = 1e-5


config = Config()
