from src.finetuning.config import config
from src.finetuning.data import load_datasets
from src.finetuning.model import setup_model
from src.finetuning.trainer_setup import get_trainer
from src.finetuning.logger import get_logger

logger = get_logger("main")


def main():
    try:
        logger.info("loading datasets...")
        datasets = load_datasets()

        logger.info("setting up model...")
        model = setup_model(config.checkpoint, config.num_labels)

        logger.info("initializing trainer...")
        trainer = get_trainer(model, datasets)

        logger.info("starting training...")
        trainer.train()
        logger.info("training complete.")

    except Exception as e:
        logger.exception("fatal error during training pipeline: %s", e)


if __name__ == "__main__":
    main()
