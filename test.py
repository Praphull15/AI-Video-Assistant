import sys
import os

print(os.listdir("./utils"))
print(os.listdir("./core"))

sys.path.append(os.path.abspath("./core"))
sys.path.append(os.path.abspath("./utils"))

from transcriber import transcribe_all
from audio_processor import process_input

from dotenv import load_dotenv
load_dotenv()   # Loads Mistral API key from .env

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions,
)

# ============================================
# INPUT
# ============================================

source = "https://www.youtube.com/watch?v=_Q-e_nczWqM&t=223s"

# Whisper auto-detects Hindi / English / Hinglish
# No Sarvam used anymore


# ============================================
# PROCESS AUDIO
# ============================================

chunks = process_input(source)


# ============================================
# TRANSCRIBE USING WHISPER
# ============================================

transcript = transcribe_all(chunks)

print("\n" + "=" * 60)
print("📝 TRANSCRIPT")
print("=" * 60)

print(
    transcript[:500] + "..."
    if len(transcript) > 500
    else transcript
)


# ============================================
# TITLE + SUMMARY
# ============================================

title = generate_title(transcript)
summary = summarize(transcript)

print("\n" + "=" * 60)
print(f"📌 TITLE: {title}")
print("=" * 60)

print("\n📋 SUMMARY")
print("-" * 60)
print(summary)


# ============================================
# EXTRACT INSIGHTS
# ============================================

action_items = extract_action_items(transcript)
decisions = extract_key_decisions(transcript)
questions = extract_questions(transcript)


# ============================================
# PRINT RESULTS
# ============================================

print("\n" + "=" * 60)
print("✅ ACTION ITEMS")
print("=" * 60)
print(action_items)

print("\n" + "=" * 60)
print("🔑 KEY DECISIONS")
print("=" * 60)
print(decisions)

print("\n" + "=" * 60)
print("❓ OPEN QUESTIONS")
print("=" * 60)
print(questions)

