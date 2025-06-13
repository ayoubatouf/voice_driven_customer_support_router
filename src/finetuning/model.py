import torch
from transformers import Wav2Vec2ForSequenceClassification
from src.finetuning.logger import get_logger

logger = get_logger("model")


def init_weights(m):
    if isinstance(m, torch.nn.Linear):
        torch.nn.init.xavier_uniform_(m.weight)
        m.bias.data.fill_(0.01)


def setup_model(checkpoint, num_labels):
    try:
        logger.info(f"loading model from checkpoint: {checkpoint}")
        model = Wav2Vec2ForSequenceClassification.from_pretrained(
            checkpoint,
            num_labels=num_labels,
            problem_type="single_label_classification",
        )
        model.classifier.apply(init_weights)
        logger.info("model loaded and weights initialized.")
        return model.to("cuda" if torch.cuda.is_available() else "cpu")
    except Exception as e:
        logger.exception("failed to initialize model: %s", e)
        raise
