from typing import List
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm
from src.inference.audio_dataset import CustomDataset
from src.inference.collate import CollateFunc
from transformers import AutoFeatureExtractor
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification


def predict(
    dataloader: DataLoader, model: torch.nn.Module, device: torch.device
) -> List[int]:
    model.to(device).eval()
    all_preds = []

    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Predicting"):
            input_values = batch["input_values"].to(device)
            attention_mask = batch.get("attention_mask")
            if attention_mask is not None:
                attention_mask = attention_mask.to(device)

            outputs = model(input_values, attention_mask=attention_mask)
            logits = outputs.logits

            preds = torch.argmax(logits, dim=-1)
            all_preds.append(preds.cpu())

    return torch.cat(all_preds).tolist()


def load_model_and_feature_extractor(model_name: str):
    feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
    model = AutoModelForAudioClassification.from_pretrained(model_name).to(
        torch.device("cuda" if torch.cuda.is_available() else "cpu")
    )
    return model, feature_extractor


def get_gender(
    model: torch.nn.Module,
    feature_extractor: AutoFeatureExtractor,
    audio_paths: List[str],
    device: torch.device,
    max_audio_len_sec: float = 5.0,
    batch_size: int = 16,
    num_workers: int = 2,
) -> List[int]:
    dataset = CustomDataset(audio_paths, max_audio_len_sec=max_audio_len_sec)
    collate_fn = CollateFunc(
        feature_extractor=feature_extractor,
        sampling_rate=feature_extractor.sampling_rate,
    )

    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=collate_fn,
        num_workers=num_workers,
        pin_memory=True,
    )

    return predict(dataloader, model, device)
