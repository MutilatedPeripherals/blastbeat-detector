from pathlib import Path
from typing import NamedTuple

import numpy as np
from numpy.fft import fft

from blastbeat_detector.downloading import download_from_youtube_as_mp3
from blastbeat_detector.extraction import extract_drums
from blastbeat_detector.plotting import plot_fft_with_markers
from blastbeat_detector.postprocessing import save_result


class LabeledSection(NamedTuple):
    start_idx: int
    end_idx: int
    snare_present: bool
    bass_drum_present: bool


def get_frequency_and_intensity_arrays(
    audio_data: np.ndarray, sample_rate: float
) -> tuple[np.ndarray, np.ndarray]:
    X = fft(audio_data)
    N = len(X)
    n = np.arange(N)
    T = N / sample_rate
    freq = n / T

    # Only keep positive frequencies
    nyquist_idx = len(freq) // 2
    freq = freq[:nyquist_idx]
    X = X[:nyquist_idx]

    return freq, np.abs(X)


def is_peak_present_around_frequency(
    freq_to_find: float,
    frequencies: np.ndarray,
    intensities: np.ndarray,
    peak_detection_band_width: float,
    peak_detection_min_area_threshold: float,
) -> bool:
    lower_bound = freq_to_find - peak_detection_band_width
    upper_bound = freq_to_find + peak_detection_band_width

    # Martins approach:  sum intensities (proxy for area under the curve), and compare with a peak_detection_min_area_threshold -> if meets thresh, it contains a peak around the freq. we're looking for
    indexes = np.where((frequencies >= lower_bound) & (frequencies <= upper_bound))[0]
    if len(indexes) == 0:
        return False

    intensity_sum = np.sum(intensities[indexes])

    return intensity_sum > peak_detection_min_area_threshold


def get_sections_labeled_by_percussion_content_from_audio(
    time: np.ndarray,
    data: np.ndarray,
    sample_rate: float,
    bass_drum_freq: float,
    snare_drum_freq: float,
    step_size_in_seconds: float,
    peak_detection_band_width: float,
    peak_detection_min_area_threshold: float,
) -> list[LabeledSection]:
    results = []

    step_size_in_samples = int(step_size_in_seconds * sample_rate)

    for start_idx in range(0, len(time), step_size_in_samples):
        end_idx = start_idx + step_size_in_samples
        data_range = data[start_idx:end_idx]

        freq, fft_magnitude = get_frequency_and_intensity_arrays(
            data_range, sample_rate
        )

        snare_present = is_peak_present_around_frequency(
            snare_drum_freq,
            freq,
            fft_magnitude,
            peak_detection_band_width,
            peak_detection_min_area_threshold,
        )
        bass_drum_present = is_peak_present_around_frequency(
            bass_drum_freq,
            freq,
            fft_magnitude,
            peak_detection_band_width,
            peak_detection_min_area_threshold,
        )

        results.append(
            LabeledSection(
                start_idx,
                end_idx,
                snare_present=snare_present,
                bass_drum_present=bass_drum_present,
            )
        )

    return results


def identify_blastbeats(
    sections: list[LabeledSection], min_hits
) -> list[tuple[int, int]]:
    blastbeat_start_idx = 0
    hits = 0
    results = []

    # Caveman approach: consider it as blast beat if a given number of consecutive labeled sections contain snare & bassdrum
    for i, section in enumerate(sections):
        # Ugly but necessary for improving the "counting" functionality. Otherwise a single long blast beat section was being counted as only 1.
        if hits >= min_hits:
            results.append((sections[blastbeat_start_idx].start_idx, section.start_idx))
            hits = 0

        if section.snare_present and section.bass_drum_present:
            if hits == 0:
                blastbeat_start_idx = i
            hits += 1
        else:
            hits = 0

    return results


def identify_bass_and_snare_frequencies(
    audio_data: np.ndarray,
    sample_rate: float,
    bass_drum_range: tuple[int, int],
    snare_range: tuple[int, int],
    debug_song_name: str | None = None,
) -> tuple[float, float]:
    # simple approach: fft over the whole song
    freq, intensities = get_frequency_and_intensity_arrays(audio_data, sample_rate)

    # find the peak in the bass drum range
    bass_drum_peak_idx = np.where(
        (freq >= bass_drum_range[0]) & (freq <= bass_drum_range[1])
    )[0]
    snare_peak_idx = np.where((freq >= snare_range[0]) & (freq <= snare_range[1]))[0]

    bass_drum_freq, snare_freq = None, None

    if bass_drum_peak_idx.size > 0:
        bass_drum_freq = freq[
            bass_drum_peak_idx[np.argmax(intensities[bass_drum_peak_idx])]
        ]
    else:
        print("Warning: No bass drum frequency found in the specified range.")

    if snare_peak_idx.size > 0:
        snare_freq = freq[snare_peak_idx[np.argmax(intensities[snare_peak_idx])]]
    else:
        print("Warning: No snare frequency found in the specified range.")

    if bass_drum_freq is None or snare_freq is None:
        raise ValueError(
            "Could not identify bass drum or snare frequencies. Please check the audio file."
        )

    if debug_song_name is not None:
        plot_fft_with_markers(
            freq,
            intensities,
            bass_drum_freq,
            snare_freq,
            bass_drum_range=bass_drum_range,
            snare_range=snare_range,
            title=debug_song_name,
        )
    return bass_drum_freq, snare_freq


def process_song(
    file_path: Path,
    peak_detection_band_width=10.0,
    peak_detection_min_area_threshold=37.6,
    step_size_in_seconds=0.15,
    bass_drum_range=(10, 100),
    snare_range=(170, 600),
    min_consecutive_hits=8
):
    output_dir = Path.cwd().resolve() / "output"
    output_dir.mkdir(exist_ok=True)

    (time, audio_data, sample_rate), drumtrack_path = extract_drums(file_path)
    bass_drum_freq, snare_freq = identify_bass_and_snare_frequencies(
        audio_data,
        sample_rate,
        bass_drum_range,
        snare_range
    )
    print(
        f"Estimated frequencies -- Bass drum: {bass_drum_freq} Hz; Snare drum: {snare_freq} Hz"
    )

    print("Identifying blast beats...")
    labeled_sections = get_sections_labeled_by_percussion_content_from_audio(
        time,
        audio_data,
        sample_rate,
        bass_drum_freq,
        snare_freq,
        step_size_in_seconds,
        peak_detection_band_width,
        peak_detection_min_area_threshold,
    )
    blastbeat_intervals = identify_blastbeats(labeled_sections, min_consecutive_hits)

    save_result(
        time, blastbeat_intervals, snare_freq, bass_drum_freq, file_path, drumtrack_path, output_dir.as_posix()
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str)
    parser.add_argument("--url", type=str)
    args = parser.parse_args()

    if args.file:
        # Mode 1:  use local file
        file_path = Path(args.file)
        if not file_path.exists():
            raise FileNotFoundError(f"The specified file does not exist: {file_path}")
    elif args.url:
        # Mode 2:  download from YouTube
        success, file_path = download_from_youtube_as_mp3(args.url)
        if not success or file_path is None:
            raise RuntimeError("Failed to download the YouTube video.")
    else:
        raise ValueError(
            "You must provide either a local file path (--file) or a url to download from YouTube (--url)"
        )

    process_song(file_path)
