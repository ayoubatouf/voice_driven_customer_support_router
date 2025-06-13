from typing import List, Dict, Union, Optional
import torch
from transformers import AutoFeatureExtractor


class CollateFunc:
    def __init__(
        self,
        feature_extractor: AutoFeatureExtractor,
        padding: Union[bool, str] = True,
        pad_to_multiple_of: Optional[int] = None,
        return_attention_mask: bool = True,
        sampling_rate: int = 16000,
        max_length: Optional[int] = None,
    ):
        self.feature_extractor = feature_extractor
        self.padding = padding
        self.pad_to_multiple_of = pad_to_multiple_of
        self.return_attention_mask = return_attention_mask
        self.sampling_rate = sampling_rate
        self.max_length = max_length

    def __call__(self, batch: List[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
        input_values = [
            (
                item["input_values"].cpu().numpy()
                if isinstance(item["input_values"], torch.Tensor)
                else item["input_values"]
            )
            for item in batch
        ]
        return self.feature_extractor(
            input_values,
            sampling_rate=self.sampling_rate,
            return_tensors="pt",
            padding=self.padding,
            pad_to_multiple_of=self.pad_to_multiple_of,
            return_attention_mask=self.return_attention_mask,
            max_length=self.max_length,
        )
