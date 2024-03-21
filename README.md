## How to use
Run `./main.py` to transcribe video(s).

The `--all` option searches for all files ending in `.R.mp4` recursively in the `DEFAULT_PATH` and transcribes them.

The default model is `small`, you may choose other models and change the min gap / threshold for speech segments as per your requirements. Refer to [whisper](https://github.com/openai/whisper) and [stable-ts](https://github.com/jianfch/stable-ts) documentation for more details.

## Dependencies
[ffmpeg](https://ffmpeg.org/download.html) and [stable-ts](https://github.com/jianfch/stable-ts). Developed on Linux, may or may not work on other platforms.
