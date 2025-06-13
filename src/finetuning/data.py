import glob
import os
from datasets import concatenate_datasets, DatasetDict
from src.finetuning.config import config
from src.finetuning.utils import parquet_to_audio_dataset, assign_genre
from src.finetuning.preprocessing import prepare_dataset
from src.finetuning.logger import get_logger

logger = get_logger("data")


def load_datasets():
    try:
        train_files = sorted(
            glob.glob(os.path.join(config.base_path, "train.clean.100-*.parquet"))
        )
        test_files = sorted(
            glob.glob(os.path.join(config.base_path, "test.clean-*.parquet"))
        )

        if not train_files:
            raise FileNotFoundError("no training files found.")
        if not test_files:
            raise FileNotFoundError("no test files found.")

        logger.info(f"found {len(train_files)} training files.")
        logger.info(f"found {len(test_files)} test files.")

        train_datasets = [
            parquet_to_audio_dataset(f, config.sampling_rate) for f in train_files
        ]
        full_train_dataset = concatenate_datasets(train_datasets).map(assign_genre)

        split = full_train_dataset.train_test_split(test_size=0.1, seed=42)
        train_dataset = split["train"]
        val_dataset = split["test"]

        test_dataset = parquet_to_audio_dataset(
            test_files[0], config.sampling_rate
        ).map(assign_genre)

        logger.info("applying feature extraction to datasets...")
        train_dataset = train_dataset.map(
            prepare_dataset, remove_columns=train_dataset.column_names, batched=False
        )
        val_dataset = val_dataset.map(
            prepare_dataset, remove_columns=val_dataset.column_names, batched=False
        )
        test_dataset = test_dataset.map(
            prepare_dataset, remove_columns=test_dataset.column_names, batched=False
        )

        logger.info("dataset preparation complete.")

        return DatasetDict(
            {
                "train": train_dataset,
                "validation": val_dataset,
                "test": test_dataset,
            }
        )

    except Exception as e:
        logger.exception("failed to load or process datasets: %s", e)
        raise
