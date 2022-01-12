#!/bin/env python3
from sys import argv as SYS_ARGS
from pydub import AudioSegment
import pathlib

WHITESPACE = ['\t', '', ' ']
SPLIT_CHAR = '|'

WAIT = False


class bcolours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def tests():
    assert (timestamp_to_milliseconds("21:37") == 1297000)


def main():
    argv = parse_args()
    print(argv)

    album: str = pathlib.PurePath(argv[0]).name.replace(".aac", "")
    print(f"album: {album}")

    song_datas = load_music_and_SongData(argv[0], argv[1])
    print("parsed song datas: ")
    for item in song_datas[1]:
        print(item)

    print("finished loading song data, waiting to start serialising songs with metadata")
    if WAIT:
        input()

    for song in song_datas[1]:
        print(f"starting to serialise {song.title}")
        song.serialise_with_metadata(song_datas[0], album=album)

    print("finished, waiting...")
    if WAIT:
        input()


class SongData:
    start_time: int = 0
    end_time: int = 0
    author: str = "author"
    title: str = "title"
    track_num: int = 0

    def __init__(self, start_time: int, author: str, title: str, track_num: int):
        self.start_time = start_time
        self.author = author
        self.title = title
        self.track_num = track_num

    def __str__(self):
        return f"start_time: {self.start_time}, end_time: {self.end_time}, author: {self.author}, title: {self.title}"

    def __repr__(self):
        return self.__str__()

    # uses self data to serialise a fragment from audio_segment with metadata
    def serialise_with_metadata(self, audio_segment: AudioSegment, album: str = ""):
        if self.start_time != 0 and self.end_time == 0:
            audio_segment[self.start_time:] \
                .export(f"{self.title}.mp3", format="mp3", tags={"artist": self.author, "album": album, "track": self.track_num + 1})
        else:
            audio_segment[self.start_time:self.end_time] \
                .export(f"{self.title}.mp3", format="mp3", tags={"artist": self.author, "album": album, "track": self.track_num + 1})


# this function loads both the music file and the SongDatas from provided source paths
def load_music_and_SongData(song_path: str, SongData_source_path: str) -> (AudioSegment, list[SongData]):
    romanised = False

    sond_datas: list[SongData] = []

    file_content = open(SongData_source_path, mode="r").read()
    track_pos: int = 0
    for line in file_content.splitlines():
        # print(line)
        if romanised:
            if not line == "":
                l = line.split(SPLIT_CHAR)
                d = l[1].split(" - ")
                sond_datas.append(SongData(timestamp_to_milliseconds(l[0]), d[0], d[1], track_pos))
                track_pos += 1
        elif line.startswith("# romanised"):
            print(f"{bcolours.OKGREEN}romanised tag found{bcolours.ENDC}")
            romanised = True

    if not romanised:
        print(f"{bcolours.WARNING}romanised tag was not found, parsing all{bcolours.ENDC}")

        for line in file_content.splitlines():
            if not line == "" or not line.startswith("#"):
                l = line.split(SPLIT_CHAR)
                d = l[1].split(" - ")
                sond_datas.append(SongData(timestamp_to_milliseconds(l[0]), d[0], d[1], track_pos))
                track_pos += 1

    for i in range(len(sond_datas) - 1):
        sond_datas[i].end_time = sond_datas[i + 1].start_time

    print("loading music file")
    print("this might take a while depending on the file size")
    splice = AudioSegment.from_file(song_path)
    # sond_datas[len(sond_datas) - 1].end_time = splice.duration_seconds * 1000

    return splice, sond_datas


# PROD
# this will die if anything goes wrong
# one might want to change this to use a try-catch block
# but one cannot be bothered to do that
# TODO: introduce a try-catch block
def timestamp_to_milliseconds(timestamp: str) -> int:
    times = timestamp.split(":")
    return (int(times[0]) * 60 + int(times[1])) * 1000


# PROD
# uses SYS_ARGS and returns argv but checked for possible issues
def parse_args() -> list[str]:
    if not SYS_ARGS[1].endswith(".aac"):
        print("an .aac file must be given as the first argument")
        exit(1)
    if not SYS_ARGS[2].endswith(".txt"):
        print("a .txt file must be given as the second argument")
        exit(2)

    return SYS_ARGS[1:]


if __name__ == "__main__":
    # run tests before doing anything else
    tests()
    main()
