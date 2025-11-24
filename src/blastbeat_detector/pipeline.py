import argparse
import csv
from pathlib import Path

from src.blastbeat_detector.downloading import download_from_youtube_as_mp3
from src.blastbeat_detector.processing import process_song


def parse_float(row, key):
    return float(row[key]) if row.get(key) else None


def parse_range(row, start, end):
    return (
        (float(row[start]), float(row[end]))
        if row.get(start) and row.get(end)
        else None
    )


def parse_int(row, key):
    return int(row[key]) if row.get(key) else None


def load_rows(csv_path):
    with open(csv_path, newline="") as f:
        return [
            r
            for r in csv.DictReader(l for l in f if not l.lstrip().startswith("#"))
            if r.get("src")
        ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    args = parser.parse_args()

    for row in load_rows(args.csv_path):
        src = row["src"].strip()
        file_path = None

        if src.startswith(("http://", "https://")):
            print(f"Processing YouTube URL: {src}")
            success, file_path = download_from_youtube_as_mp3(src)
            if not success or not file_path:
                print(f"Failed to download: {src}")
                continue
        else:
            file_path = Path(src)
            if not file_path.exists():
                print(f"File does not exist: {file_path}")
                continue

        kwargs = {
            k: v
            for k, v in {
                "peak_detection_band_width": parse_float(
                    row, "peak_detection_band_width"
                ),
                "peak_detection_min_area_threshold": parse_float(
                    row, "peak_detection_min_area_threshold"
                ),
                "step_size_in_seconds": parse_float(row, "step_size_in_seconds"),
                "bass_drum_range": parse_range(
                    row, "bass_drum_range_start", "bass_drum_range_end"
                ),
                "snare_range": parse_range(
                    row, "snare_drum_range_start", "snare_drum_range_end"
                ),
                "min_consecutive_hits": parse_int(row, "min_consecutive_hits"),
            }.items()
            if v is not None
        }

        process_song(file_path, **kwargs)
        print("-----")
