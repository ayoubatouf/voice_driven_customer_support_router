import pyarrow.parquet as pq
from datasets import Dataset, Audio


def parquet_to_audio_dataset(filepath: str, sampling_rate: int = 16000) -> Dataset:
    df = pq.read_table(filepath).to_pandas()
    ds = Dataset.from_pandas(df).cast_column(
        "audio", Audio(sampling_rate=sampling_rate)
    )
    return ds


def assign_genre(example):
    example["genre"] = int(example["speaker_id"] >= 3000)
    return example
