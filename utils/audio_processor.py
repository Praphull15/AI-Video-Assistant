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

        # 🎯 OPTIONAL COOKIE SUPPORT (only if provided)
        # prevents your chrome error completely
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

            title = info.get("title", "audio").replace("/", "_")
            final_path = os.path.join(DOWNLOAD_DIR, f"{title}.wav")

        return final_path

    except Exception as e:
        print("❌ Download failed:", str(e))
        return None


# -------------------------
# Convert to WAV
# -------------------------
def convert_to_wav(input_path: str) -> str:

    output_path = os.path.splitext(input_path)[0] + "_converted.wav"

    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)

    audio.export(output_path, format="wav")

    return output_path


# -------------------------
# Chunk Audio
# -------------------------
def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:

    audio = AudioSegment.from_wav(wav_path)

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
            return []

    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)

    print(f"Audio ready — {len(chunks)} chunk(s) created.")

    return chunks