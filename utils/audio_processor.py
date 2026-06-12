import os
from pydub import AudioSegment
import yt_dlp
import imageio_ffmpeg

# -------------------------
# Setup
# -------------------------
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# -------------------------
# YouTube Downloader (HYBRID SAFE)
# -------------------------
def download_youtube_audio(url: str, cookiefile: str = None) -> str:

    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "ffmpeg_location": ffmpeg_path,

        # ✅ SAFE HEADERS (always works)
        "http_headers": {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.youtube.com/",
        },

        "noplaylist": True,
        "retries": 10,
        "fragment_retries": 10,

        # ✅ FIX: avoids HTTP 403 Forbidden on Streamlit Cloud by using
        # YouTube's android client for extraction (web client often
        # gets blocked from cloud IPs).
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
            }
        },

        # 🎯 OPTIONAL COOKIE SUPPORT (only if provided)
        **({"cookiefile": cookiefile} if cookiefile else {}),

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],

        "quiet": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            # ✅ FIX: use yt-dlp's actual prepared filename instead of
            # guessing from info["title"]. yt-dlp sanitizes filenames
            # (removes/replaces special chars, emojis, unicode etc.)
            # differently than a simple .replace("/", "_"), so the
            # manually-built path often doesn't match the real file.
            downloaded_path = ydl.prepare_filename(info)

            # After FFmpegExtractAudio postprocessor runs, the file
            # extension becomes .wav (the original ext is replaced).
            base, _ = os.path.splitext(downloaded_path)
            final_path = base + ".wav"

        # ✅ FIX: verify the file actually exists before returning it.
        if not os.path.exists(final_path):
            print(f"❌ Expected output file not found: {final_path}")

            # Fallback: sometimes the postprocessor keeps a slightly
            # different name. Try to find any .wav file with a matching
            # base name in the downloads dir as a last resort.
            dir_name = os.path.dirname(final_path) or "."
            base_name = os.path.basename(base)
            for f in os.listdir(dir_name):
                if f.startswith(base_name) and f.endswith(".wav"):
                    fallback_path = os.path.join(dir_name, f)
                    print(f"✅ Found fallback file: {fallback_path}")
                    return fallback_path

            return None

        return final_path

    except Exception as e:
        print("❌ Download failed:", str(e))
        return None


# -------------------------
# Convert to WAV
# -------------------------
def convert_to_wav(input_path: str) -> str:

    if not os.path.exists(input_path):
        print(f"❌ Input file not found: {input_path}")
        return None

    output_path = os.path.splitext(input_path)[0] + "_converted.wav"

    try:
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(output_path, format="wav")
    except Exception as e:
        print("❌ Audio conversion failed:", str(e))
        return None

    return output_path


# -------------------------
# Chunk Audio
# -------------------------
def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:

    if not wav_path or not os.path.exists(wav_path):
        print(f"❌ Cannot chunk audio, file not found: {wav_path}")
        return []

    try:
        audio = AudioSegment.from_wav(wav_path)
    except Exception as e:
        print("❌ Failed to load wav file:", str(e))
        return []

    chunk_ms = chunk_minutes * 60 * 1000
    chunks = []

    base_name = os.path.splitext(wav_path)[0]

    for i, start in enumerate(range(0, len(audio), chunk_ms)):

        chunk = audio[start:start + chunk_ms]
        chunk_path = f"{base_name}_chunk_{i}.wav"

        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks


# -------------------------
# Main Pipeline (SMART)
# -------------------------
def process_input(source: str, cookiefile: str = None) -> list:

    if source.startswith("http"):
        print("Detected YouTube URL. Downloading audio...")

        wav_path = download_youtube_audio(source, cookiefile=cookiefile)

        if wav_path is None:
            print("❌ process_input: download step returned no file. Aborting.")
            return []

    else:
        print("Detected local file. Converting to WAV...")

        if not os.path.exists(source):
            print(f"❌ process_input: local file not found: {source}")
            return []

        wav_path = convert_to_wav(source)

        if wav_path is None:
            print("❌ process_input: conversion step failed. Aborting.")
            return []

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)

    if not chunks:
        print("❌ process_input: no chunks produced. Aborting.")
        return []

    print(f"Audio ready — {len(chunks)} chunk(s) created.")

    return chunks