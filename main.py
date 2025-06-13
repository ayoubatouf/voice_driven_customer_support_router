from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.agent.agent_routing import find_agent, get_agent_info
from src.agent.database import SessionLocal
from src.inference.models import (
    analyze_audio,
    load_emotion_classifier,
    load_gender_classifier,
    load_intent_classifier,
    load_translation_model,
    load_whisper_model,
)
import tempfile
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # !!!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


whisper_model = load_whisper_model()
translation_tokenizer, translation_model = load_translation_model()
intent_classifier = load_intent_classifier()
emotion_classifier = load_emotion_classifier()
gender_feature_extractor, gender_model = load_gender_classifier()


@app.post("/route-customer-to-agent/")
async def route_customer_to_agent(file: UploadFile = File(...)):
    # whisper requires the path to the audio file not bytes
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=os.path.splitext(file.filename)[1]
    ) as tmp:
        temp_path = tmp.name
        while chunk := await file.read(1024 * 1024):
            tmp.write(chunk)

    try:
        metadata = analyze_audio(
            temp_path,
            whisper_model,
            gender_model,
            gender_feature_extractor,
            translation_tokenizer,
            translation_model,
            intent_classifier,
            emotion_classifier,
        )
    finally:
        try:
            os.remove(temp_path)
        except FileNotFoundError:
            pass

    intent_result = metadata.get("intent", {})
    intent_label = (
        intent_result.get("labels", [None])[0]
        if isinstance(intent_result, dict)
        else intent_result or ""
    )

    with SessionLocal() as db:
        agent_id = find_agent(
            metadata["language"], intent_label, metadata["gender"], db
        )
        if agent_id is None:
            raise HTTPException(status_code=404, detail="no available agent found")

        agent_info = get_agent_info(agent_id, db)
        if not agent_info:
            raise HTTPException(
                status_code=500, detail="matched agent record not found"
            )

    print(f"matched agent: {agent_info}, metadata: {metadata}")

    return JSONResponse(content={"analysis": metadata, "assigned_agent": agent_info})
