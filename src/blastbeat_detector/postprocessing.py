import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from pydub import AudioSegment


def compress_to_mp3(wav_path: Path, bitrate: str = "192k") -> Path:
    mp3_path = wav_path.with_suffix(".mp3")
    audio = AudioSegment.from_wav(wav_path)
    audio.export(mp3_path, format="mp3", bitrate=bitrate)
    return mp3_path


def save_result(
    time: np.ndarray,
    ranges_to_highlight: list[tuple[int, int]],
    snare_frequency: float,
    bass_drum_frequency: float,
    filepath: Path,
    drumtrack_path: Path,
    output_dir: str,
):
    output = {
        "blast_beats": [],
        "snare_frequency": snare_frequency,
        "bass_drum_frequency": bass_drum_frequency,
    }

    for start, end in ranges_to_highlight:
        output["blast_beats"].append(
            {"start_time": float(time[start]), "end_time": float(time[end - 1])}
        )

    mp3_drumtrack_path = compress_to_mp3(drumtrack_path)

    zip_path = f"{output_dir}/{filepath.stem.replace(' ', '_').replace('-', '_')}.zip"
    with ZipFile(zip_path, "w") as zipf:
        zipf.writestr(
            f"{filepath.stem.replace(' ', '_').replace('-', '_')}.json",
            json.dumps(output, indent=4),
        )
        zipf.write(filepath, arcname=filepath.name)
        zipf.write(mp3_drumtrack_path, arcname=mp3_drumtrack_path.name)

    print(f"Exported results to: {zip_path}")
    return zip_path
