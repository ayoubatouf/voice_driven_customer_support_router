import torch
from transformers import Wav2Vec2FeatureExtractor
from src.finetuning.config import config

feature_extractor = Wav2Vec2FeatureExtractor(
    do_normalize=True,
    feature_size=1,
    padding_side="right",
    padding_value=0,
    return_attention_mask=True,
    sampling_rate=config.sampling_rate,
)


def prepare_dataset(batch):
    inputs = feature_extractor(
        batch["audio"]["array"],
        sampling_rate=batch["audio"]["sampling_rate"],
        return_tensors="pt",
    )
    return {
        "input_values": inputs.input_values[0].numpy(),
        "label": int(batch["genre"]),
    }


def data_collator(features):
    input_values = [torch.tensor(f["input_values"]) for f in features]
    labels = torch.tensor([f["label"] for f in features])
    batch = feature_extractor.pad(
        {"input_values": input_values}, return_tensors="pt", padding=True
    )
    batch["labels"] = labels
    return batch
