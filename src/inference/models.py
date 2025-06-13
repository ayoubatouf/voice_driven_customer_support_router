import torch
import whisper
from src.inference.predict import get_gender
from transformers import (
    MarianMTModel,
    MarianTokenizer,
    pipeline,
    AutoFeatureExtractor,
    AutoModelForAudioClassification,
)
from pathlib import Path

device = "cuda" if torch.cuda.is_available() else "cpu"
ROOT_PATH = Path(__file__).resolve().parent.parent.parent

# use "tiny" for speed !
def load_whisper_model(model_name="base"):
    return whisper.load_model(model_name)


def load_translation_model(
    local_path = ROOT_PATH / "models" / "translation",
):
    tokenizer = MarianTokenizer.from_pretrained(local_path)
    model = MarianMTModel.from_pretrained(local_path).to(device)
    return tokenizer, model


def load_gender_classifier(local_path = ROOT_PATH / "models" / "gender"):
    feature_extractor = AutoFeatureExtractor.from_pretrained(local_path)
    model = AutoModelForAudioClassification.from_pretrained(local_path).to(device)
    return feature_extractor, model


def load_intent_classifier(local_path = ROOT_PATH / "models" / "intent"):
    return pipeline(
        "zero-shot-classification",
        model=local_path,
        device=0 if device == "cuda" else -1,
        framework="pt",
    )


def load_emotion_classifier(
    local_path = ROOT_PATH / "models" / "emotion",
):
    return pipeline(
        "text-classification",
        model=local_path,
        return_all_scores=True,
        device=0 if device == "cuda" else -1,
        framework="pt",
    )


def transcribe_audio(file_path, whisper_model):
    result = whisper_model.transcribe(file_path, verbose=False)
    return result["language"], result["text"]


def translate_to_english(text, tokenizer, model):
    inputs = tokenizer([text], return_tensors="pt", padding=True).to(device)
    translated_tokens = model.generate(**inputs)
    translated_text = tokenizer.decode(
        translated_tokens[0],
        skip_special_tokens=True,
        clean_up_tokenization_spaces=True,
    )
    return translated_text


def classify_intent(
    text,
    classifier,
    candidate_labels=[
        "product inquiry",
        "technical support",
        "billing issue",
        "complaint",
        "feedback",
        "account cancellation",
        "order status",
        "refund request",
        "appointment scheduling",
        "service activation",
        "farewell",
    ],
):
    if not text.strip():
        return {"sequence": "", "labels": ["complaint"], "scores": []}
    try:
        return classifier(text, candidate_labels)
    except Exception as e:
        raise RuntimeError(f"Intent classification failed: {e}")


def detect_emotions(text, emotion_classifier):
    results = emotion_classifier(text)
    return results[0]


def analyze_audio(
    file,
    whisper_model,
    gender_model,
    feature_extractor,
    translation_tokenizer,
    translation_model,
    intent_classifier,
    emotion_classifier,
):

    language, transcript = transcribe_audio(file, whisper_model)

    gender_result = get_gender(gender_model, feature_extractor, [file], device)[0]
    gender_label = "Male" if gender_result == 1 else "Female"

    if language != "en":
        translated_text = translate_to_english(
            transcript, translation_tokenizer, translation_model
        )
    else:
        translated_text = transcript

    intent_result = classify_intent(translated_text, intent_classifier)

    emotion_result = detect_emotions(translated_text, emotion_classifier)

    return {
        "audio_file": file,
        "language": language,
        "transcription": transcript,
        "gender": gender_label,
        "translation": translated_text,
        "intent": intent_result,
        "emotion": emotion_result,
    }
