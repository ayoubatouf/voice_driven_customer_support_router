import torch
from src.inference.predict import get_gender, load_model_and_feature_extractor


if __name__ == "__main__":
    model_name = "alefiury/wav2vec2-large-xlsr-53-gender-recognition-librispeech"
    model, feature_extractor = load_model_and_feature_extractor(model_name)
    audio_files = ["male.wav", "female.wav"]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    predictions = get_gender(model, feature_extractor, audio_files, device)
    print("predicted labels:", predictions)
