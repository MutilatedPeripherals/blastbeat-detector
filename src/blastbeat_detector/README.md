
## Local development

### Install deps

```bash
# 1. Install python requirements
python -m venv venv
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
