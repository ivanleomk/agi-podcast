"""Mix speech audio and background music into a polished radio show file."""

import argparse
import os
from pathlib import Path

from pydub import AudioSegment


def load_speech(workspace: Path) -> AudioSegment:
    """Load speech audio from workspace."""
    speech_path = workspace / "audio" / "speech_partial.wav"
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


def main():
    parser = argparse.ArgumentParser(description="Mix speech and music into a podcast episode")
    parser.add_argument("--workspace", default=".", help="Root workspace directory")
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


if __name__ == "__main__":
    main()
