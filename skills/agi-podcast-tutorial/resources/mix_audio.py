"""Mix speech audio and background music into a polished radio show file."""

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

from pydub import AudioSegment


GCS_BUCKET = "agi-podcast-audio"


def load_speech(workspace: Path) -> AudioSegment:
    """Load speech audio from workspace."""
    speech_path = workspace / "audio" / "speech.wav"
    if not speech_path.exists():
        raise FileNotFoundError(f"Speech file not found: {speech_path}")

    print(f"📖 Loading speech from {speech_path}")
    speech = AudioSegment.from_wav(str(speech_path))
    print(f"   Duration: {len(speech) / 1000:.1f}s")
    return speech


def load_music(workspace: Path) -> AudioSegment | None:
    """Load background music if it exists."""
    music_path = workspace / "audio" / "music" / "background.mp3"
    if not music_path.exists():
        print("⚠️  No background music found, producing speech-only output")
        return None

    print(f"🎵 Loading music from {music_path}")
    music = AudioSegment.from_mp3(str(music_path))
    print(f"   Duration: {len(music) / 1000:.1f}s")
    return music


def mix(speech: AudioSegment, music: AudioSegment | None) -> AudioSegment:
    """Mix speech and music together."""

    # Pad 3s silence at end of speech so fade-out doesn't cut into speech
    silence = AudioSegment.silent(duration=3000)
    padded_speech = speech + silence
    total_duration = len(padded_speech)

    if music is None:
        # Speech-only: just apply fade-in/fade-out
        result = padded_speech.fade_in(500).fade_out(2000)
        print(f"🎙️  Speech-only output: {total_duration / 1000:.1f}s")
        return result

    # 1s music intro before speech starts
    music_intro_ms = 1000
    target_music_duration = total_duration + music_intro_ms

    # Loop music to cover full duration
    loops_needed = (target_music_duration // len(music)) + 1
    looped_music = music * loops_needed
    looped_music = looped_music[:target_music_duration]

    # Lower music volume to -18dB
    looped_music = looped_music - 18

    # Apply music fade-in (3s) and fade-out (5s)
    looped_music = looped_music.fade_in(3000).fade_out(5000)

    # Overlay speech onto music after 1s intro
    mixed = looped_music.overlay(padded_speech, position=music_intro_ms)

    # Overall fade-in/fade-out
    mixed = mixed.fade_in(500).fade_out(2000)

    print(f"🎛️  Mixed output: {len(mixed) / 1000:.1f}s")
    return mixed


def upload_to_gcs(local_path: Path, gcs_key_path: str) -> str:
    """Upload file to GCS and return public URL."""
    import json
    from google.cloud import storage
    from google.oauth2 import service_account

    with open(gcs_key_path, "r", encoding="utf-8") as f:
        info = json.load(f)

    private_key = info.get("private_key", "")
    if private_key:
        header = "-----BEGIN PRIVATE KEY-----"
        footer = "-----END PRIVATE KEY-----"
        # Extract base64 body and remove any existing whitespaces/newlines
        body = private_key.replace(header, "").replace(footer, "").strip()
        body = "".join(body.split())
        # Format into standard 64-character chunks
        lines = [body[i:i+64] for i in range(0, len(body), 64)]
        # Re-assemble standard PEM
        info["private_key"] = f"{header}\n" + "\n".join(lines) + f"\n{footer}\n"

    credentials = service_account.Credentials.from_service_account_info(info)
    client = storage.Client(credentials=credentials)
    bucket = client.bucket(GCS_BUCKET)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    blob_name = f"episodes/ai_radio_{timestamp}.mp3"

    blob = bucket.blob(blob_name)
    blob.upload_from_filename(str(local_path), content_type="audio/mpeg")

    public_url = f"https://storage.googleapis.com/{GCS_BUCKET}/{blob_name}"
    return public_url


def main():
    parser = argparse.ArgumentParser(description="Mix speech and music into a podcast episode")
    parser.add_argument("--workspace", default=".", help="Root workspace directory")
    parser.add_argument("--upload", action="store_true", help="Upload to GCS after mixing")
    parser.add_argument("--gcs-key", default=os.environ.get("GOOGLE_GCS_KEY_PATH", ""),
                        help="Path to GCS service account JSON key")
    args = parser.parse_args()

    workspace = Path(args.workspace)

    speech = load_speech(workspace)
    music = load_music(workspace)
    result = mix(speech, music)

    # Export
    out_dir = workspace / "audio" / "final"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ai_radio.mp3"

    print(f"💾 Exporting to {out_path}")
    result.export(str(out_path), format="mp3", bitrate="192k")

    file_size = os.path.getsize(out_path)
    print(f"✅ Done! {file_size / 1024:.0f} KB")

    # Upload if requested
    if args.upload:
        gcs_key = args.gcs_key
        if not gcs_key:
            print("❌ --gcs-key or GOOGLE_GCS_KEY_PATH required for upload")
            return

        print(f"☁️  Uploading to GCS...")
        url = upload_to_gcs(out_path, gcs_key)
        print(f"🔗 {url}")


if __name__ == "__main__":
    main()
