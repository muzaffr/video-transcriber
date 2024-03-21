#!/usr/bin/env python

from argparse import ArgumentParser
from glob import iglob
from json import load as jload
from os import mkdir, path
from shutil import rmtree, copy2 as copyfile
from subprocess import run
from typing import List, Tuple
from uuid import uuid4
from warnings import simplefilter

from numba.core.errors import NumbaDeprecationWarning, NumbaPendingDeprecationWarning
simplefilter('ignore', category=NumbaDeprecationWarning)
simplefilter('ignore', category=NumbaPendingDeprecationWarning)

import stable_whisper

class Transcriber:

    def __init__(self) -> None:
        self._out_dir: str = str(uuid4())

    def _create_out_dir(self) -> None:
        '''Create a random-named output directory in the current folder.'''
        mkdir(self._out_dir)

    def _convert_to_mp3(self, input_: str) -> None:
        '''Convert the input video to audio and store it.
        Parameters:
            input_: Path to input video.
        Returns:
            None
        Generates:
            audio.mp3 in the output folder.
        '''
        run(f'ffmpeg -y -i {input_} {self._out_dir}/audio.mp3'.split(), capture_output=True)

    def _load_model(self) -> None:
        '''Load the Whisper stable-ts model.'''
        self._model = stable_whisper.load_model('small')

    def _write_transcription(self) -> None:
        '''Format and write the transcription to a text file.
        Parameters:
            None
        Returns:
            None
        Generates:
            transcription.txt in the output folder.
        '''
        min_gap = 2.0   # seconds, between two speech segments to split them
        result = self._model.transcribe(f'{self._out_dir}/audio.mp3', regroup=f'ms_sg={min_gap}')
        result.save_as_json(f'{self._out_dir}/transcription.json')
        with open(f'{self._out_dir}/transcription.json', 'r') as jsonfile:
            chunks = [(seg['start'], seg['end'], seg['text'],) for seg in jload(jsonfile)['segments']]
        with open(f'{self._out_dir}/transcription.txt', 'w') as outfile:
            outfile.writelines([f'[{int(start/60):02d}:{start%60:05.2f} - '
                                f'{int(end/60):02d}:{end%60:05.2f}] {text}\n\n' for
                                (start, end, text) in chunks])

    def _cleanup(self) -> None:
        '''Delete intermediate files.'''
        rmtree(self._out_dir)

    def transcribe(self, input_: str) -> None:
        '''Transcribe.'''
        print(f'\nTranscribing: {input_}...')
        self._create_out_dir()
        self._convert_to_mp3(input_)
        self._load_model()
        self._write_transcription()
        copyfile(f'{self._out_dir}/transcription.txt', input_.rsplit('.', 2)[0] + '.T.txt')
        self._cleanup()


def get_unprocessed_files(dirpath):
    for filename in iglob(f'{dirpath}/**/*.R.mp4', recursive=True):
        if not path.isfile(filename.replace('.R.mp4', '.T.txt')):
            yield filename


def main():
    parser = ArgumentParser(description='Transcribe')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', '-f', type=str)
    group.add_argument('--all', '-a', action='store_true')
    args = parser.parse_args()
    transcriber = Transcriber()
    DEFAULT_PATH = '/mnt/d'
    if args.file:
        transcriber.transcribe(args.file)
    elif args.all:
        for filename in get_unprocessed_files(DEFAULT_PATH):
            transcriber.transcribe(filename)


if __name__ == '__main__':
    main()
