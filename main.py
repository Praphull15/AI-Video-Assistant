import sys
import os

sys.path.append(os.path.abspath("./core"))
sys.path.append(os.path.abspath("./utils"))

from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()


def run_pipeline(source: str, language: str = "english") -> dict:
    print("starting AI Video Assistant")

    # -------------------------------------------------
    # Step 1: Get audio chunks (download/convert/split)
    # -------------------------------------------------
    chunks = process_input(source)

    # ✅ FIX: fail fast if audio processing produced nothing,
    # instead of silently continuing with empty data.
    if not chunks:
        raise RuntimeError(
            "Audio processing failed: no audio chunks were produced. "
            "Check the logs above for the download/conversion error "
            "(e.g. yt-dlp download failure or invalid local file path)."
        )

    # -------------------------------------------------
    # Step 2: Transcribe
    # -------------------------------------------------
    transcript = transcribe_all(chunks, language)
    print(f"raw transcription (first 300 characters): {transcript[:300]}")

    # ✅ FIX: fail fast if transcript is empty.
    if not transcript or not transcript.strip():
        raise RuntimeError(
            "Transcription failed: transcript is empty. "
            "Check the Whisper model and the audio chunk files."
        )

    # -------------------------------------------------
    # Step 3: Title + Summary
    # -------------------------------------------------
    title = generate_title(transcript)
    summary = summarize(transcript)

    # -------------------------------------------------
    # Step 4: Action items / decisions / questions
    # -------------------------------------------------
    action_item = extract_action_items(transcript)
    decisions = extract_key_decisions(transcript)
    questions = extract_questions(transcript)

    # -------------------------------------------------
    # Step 5: RAG chain
    # -------------------------------------------------
    rag_chain = build_rag_chain(transcript)

    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_item,
        "key_decisions": decisions,
        "open_questions": questions,
        "rag_chain": rag_chain,
    }


if __name__ == "__main__":
    # CLI entry point
    source = input("Enter YouTube URL or local file path: ").strip()
    language = input("Language (english/hinglish): ").strip() or "english"

    try:
        result = run_pipeline(source, language)
    except RuntimeError as e:
        print(f"\n❌ Pipeline stopped: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print(f"📌 Title: {result['title']}")
    print(f"\n📋 Summary:\n{result['summary']}")
    print(f"\n✅ Action Items:\n{result['action_items']}")
    print(f"\n🔑 Key Decisions:\n{result['key_decisions']}")
    print(f"\n❓ Open Questions:\n{result['open_questions']}")
    print("=" * 60)

    # Phase 2 — Chat with your meeting via RAG
    print("\n💬 Chat with your meeting (type 'exit' to quit)\n")
    rag_chain = result["rag_chain"]
    while True:
        question = input("You: ").strip()
        if question.lower() in ["exit", "quit", "q"]:
            print("👋 Goodbye!")
            break
        if not question:
            continue
        answer = ask_question(rag_chain, question)
        print(f"\n🤖 Assistant: {answer}\n")