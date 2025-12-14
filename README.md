# Blast beat detector

[![Tests](https://github.com/MutilatedPeripherals/blastbeat-counter/actions/workflows/run-tests.yml/badge.svg)](https://github.com/MutilatedPeripherals/blastbeat-counter/actions/workflows/run-tests.yml)

## Premise

What is a blast beat? This is what wikipedia has to say:
> A blast beat is a type of drum beat that originated in hardcore punk and grindcore, and is often associated with
> certain styles of extreme metal, namely black metal, death metal and their respective subgenres. The blast-beat
> generally comprises a repeated, sixteenth-note figure
> played
> at a very fast tempo, and divided uniformly among the bass drum, snare, and ride, crash, or hi-hat cymbal."

As metal maniacs and programmers, we naturally asked ourselves:
**_Can we identify blast beats programmatically?_**

## Experiments

We took one of the cleanest blast-beat examples available, in terms of production & execution (_Dying Fetus - Subjected
to a Beating_), and after isolating the drums and analyzing the spectrogram, we observed a very clear pattern, with the
**bass drum** hits hovering around **60Hz** and the **snare** around around **300Hz**.

Here we highlighted the first blast beat of this song, between 29s - 31s:

<img width="100%" alt="audacity_analysis" src="https://github.com/user-attachments/assets/7920a83f-4aa1-45a6-b9cb-cded0658a64c" />

### Preliminary results

Here is what we are currently detecting with the MVP (blast beats in red):

<img width="100%" alt="Dying_Fetus___Subjected_To_A_Beating" src="https://github.com/user-attachments/assets/51f43e78-fad6-4ffc-b7aa-c7d2f46c239f" />

And here is another one, from the ecuadorian band Curetaje:

<img width="100%" alt="CURETAJE___Arutam" src="https://github.com/user-attachments/assets/8a6c01b2-eb8a-4461-af2b-d6628d6e016b" />

(Yes, in this one the end is all blast beats)

## Demo

Currently the detector is not deployed as a service because demucs requires a GPU for drum-track separation in
reasonable time, and those servers aren't free...

But you can:

- Try this notebook to process some songs using Google's free-tier
  GPUs: <a target="_blank" href="https://colab.research.google.com/gist/linomp/9a3cc6bfeda5ef3a09358ea29cc5363c/blastbeat_detector_notebook.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
  </a>

- Or just directly download examples of processed songs
  from [here](https://drive.google.com/drive/folders/1YFoxrsrBo8hl0cOYkdxCsfW_bf3CX7Al)

And then upload the results to the [visualizer](https://mutilatedperipherals.github.io/blastbeat-counter/):


<img width="100%" alt="image" src="https://github.com/user-attachments/assets/22f55e81-60d2-4549-bca7-bc75b09b01ff" />

## Local development

### Install deps

```bash
# 1. Install python requirements
python - m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Install ffmpeg. This is how to do it on Ubuntu:
sudo apt-get update
apt-get install ffmpeg
```

### Specify the input files & run the code

1. Create a `csv` file to pass as input to the `pipeline.py` file.

   The only mandatory column is `src`, with the file paths of the songs to analyze. Youtube URLs are also supported on a
   best-effort basis (uses `yt-dlp` to download the audio).

   Example:

    ```csv
    src
    /home/linomp/Downloads/CURETAJE - Arutam.mp3
    https://youtu.be/dQw4w9WgXcQ?si=J-UoAhM54KQGR6eW
    ```

    <details>
    <summary>Additional fields (advanced)</summary>
    Other fields are supported for debugging & development, with the most important one being `step_size_in_seconds`, which determines the size of the segments on which the song is split & analized (default value: 0.15s). 

   In `pipeline.py` you can see all the configurable fields. If left blank or unspecified, defaults will be used.

   Here is an example specifying an extra field:

    ```csv
    src,step_size_in_seconds
    /home/linomp/Downloads/CURETAJE - Arutam.mp3
    ./tmp/DER WEG EINER FREIHEIT - Ruhe (Tobias Schuler Drum Playthrough).mp3,0.1
    ./tmp/Deceso.mp3,0.18
    ```
    </details>

2. Point to the csv file & run it
    ```bash
    pipeline.py ./songs.csv
    ```
