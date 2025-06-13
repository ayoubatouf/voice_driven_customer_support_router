import torch
from transformers import TrainingArguments, Trainer
from src.finetuning.config import config
from src.finetuning.preprocessing import data_collator
from src.finetuning.evaluation import compute_metrics
from src.finetuning.logger import get_logger

logger = get_logger("trainer")


def get_trainer(model, datasets):
    logger.info("creating training arguments...")
    training_args = TrainingArguments(
        output_dir=config.output_dir,
        per_device_train_batch_size=config.batch_size,
        per_device_eval_batch_size=config.batch_size,
        num_train_epochs=config.num_epochs,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_steps=100,
        learning_rate=config.learning_rate,
        warmup_ratio=0.1,
        save_total_limit=2,
        fp16=torch.cuda.is_available(),
        report_to=[],
        dataloader_num_workers=4,
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
    )

    logger.info("training arguments ready. Initializing Trainer...")
    return Trainer(
        model=model,
        args=training_args,
        train_dataset=datasets["train"],
        eval_dataset=datasets["validation"],
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )
