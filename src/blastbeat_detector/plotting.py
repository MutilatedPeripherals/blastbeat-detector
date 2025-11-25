import matplotlib.pyplot as plt
import numpy as np


def plot_waveform_with_highlights(
    time: np.ndarray,
    data: np.ndarray,
    ranges_to_highlight: list[tuple[int, int]],
    title: str,
    output_dir:str,
):
    highlighted_time_elements = []
    highlighted_data_elements = []
    non_highlighted_time_elements = []
    non_highlighted_data_elements = []

    curr_idx = 0

    for start, end in ranges_to_highlight:
        non_highlighted_time_elements.extend(time[curr_idx:start])
        non_highlighted_data_elements.extend(data[curr_idx:start])

        highlighted_time_elements.extend(time[start:end])
        highlighted_data_elements.extend(data[start:end])

        curr_idx = end

    if curr_idx < len(time):
        non_highlighted_time_elements.extend(time[curr_idx:])
        non_highlighted_data_elements.extend(data[curr_idx:])

    fig, ax1 = plt.subplots(1, 1, figsize=(12, 8))
    ax1.scatter(
        non_highlighted_time_elements,
        non_highlighted_data_elements,
        color="blue",
        marker="o",
        label="Other",
        s=0.01,
    )
    ax1.scatter(
        highlighted_time_elements,
        highlighted_data_elements,
        color="red",
        marker="o",
        label="Blast-beats",
        s=0.01,
    )
    ax1.set_xticks(np.arange(0, time[-1] + 1, 15))
    ax1.xaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"{int(x // 60)}:{int(x % 60):02d}")
    )
    ax1.set_xlim(time[0], time[-1])
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Amplitude")

    fig.suptitle(title, fontsize=14)
    plt.tight_layout()
    plt.savefig(
        f"{output_dir}/{title.replace(" ", "_").replace("-","_")}.png",
        dpi=150,
        bbox_inches="tight",
    )
    return fig


def plot_fft_with_markers(
    freq: np.ndarray,
    fft_magnitude: np.ndarray,
    bass_drum_freq: float,
    snare_drum_freq: float,
    output_dir: str,
    title: str = "identified_freqs",
    bass_drum_range: tuple[int, int] | None = None,
    snare_range: tuple[int, int] | None = None,
):
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))

    ax.plot(freq, fft_magnitude, linewidth=1)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude")
    ax.set_ylim(1e0, fft_magnitude.max() * 1.1)
    ax.set_xlim(0, snare_range[1] + 10)
    ax.grid(True, alpha=0.3)

    ax.set_xticks(np.arange(0, snare_range[1] + 20, 20))

    if bass_drum_range:
        ax.axvspan(
            bass_drum_range[0],
            bass_drum_range[1],
            color="red",
            alpha=0.1,
            label="Bass Drum Range",
        )
    if snare_range:
        ax.axvspan(
            snare_range[0],
            snare_range[1],
            color="green",
            alpha=0.1,
            label="Snare Drum Range",
        )

    ax.axvline(
        x=bass_drum_freq,
        color="red",
        linestyle="--",
        label=f"Bass Drum Freq ({bass_drum_freq:.1f} Hz)",
    )
    ax.axvline(
        x=snare_drum_freq,
        color="green",
        linestyle="--",
        label=f"Snare Drum Freq ({snare_drum_freq:.1f} Hz)",
    )
    ax.legend()

    fig.suptitle(title, fontsize=14)
    plt.tight_layout()
    plt.savefig(
        f"{output_dir}/{title.replace(' ', '_').replace('-','_')}.png",
        dpi=150,
        bbox_inches="tight",
    )
    return fig
