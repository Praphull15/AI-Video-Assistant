import whisper
import os

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")

_model = None


# ----------------------------
# Load Whisper model once
# ----------------------------
def load_model():

    global _model

    if _model is None:

        print(f"Loading Whisper model: {WHISPER_MODEL} ...")

        _model = whisper.load_model(WHISPER_MODEL)

        print("Whisper model loaded.")

    return _model


# ----------------------------
# Transcribe single chunk
# ----------------------------
def transcribe_chunk(chunk_path: str, language: str = "english") -> str:

    model = load_model()

    result = model.transcribe(
        chunk_path,
        task="transcribe",
        fp16=False
    )

    return result["text"]



# ----------------------------
# Transcribe all chunks
# ----------------------------
def transcribe_all(chunks: list[str], language="english") -> str:

    full_transcript = ""

    for i, chunk in enumerate(chunks):

        print(f"Transcribing chunk {i + 1}/{len(chunks)}...")

        text = transcribe_chunk(chunk, language)

        full_transcript += text + " "

    print("Transcription complete.")

    return full_transcript.strip()