

import math
import sys
import subprocess
import os
import shutil
from moviepy.editor import AudioClip, VideoFileClip, concatenate_videoclips


def find_speaking(audio_clip, window_size=0.1, volume_threshold=0.01, ease_in=0.25):

    num_windows = math.floor(audio_clip.end/window_size)
    window_is_silent = []
    for i in range(num_windows):
        s = audio_clip.subclip(i * window_size, (i + 1) * window_size)
        v = s.max_volume()
        window_is_silent.append(v < volume_threshold)

    speaking_start = 0
    speaking_end = 0
    speaking_intervals = []
    for i in range(1, len(window_is_silent)):
        e1 = window_is_silent[i - 1]
        e2 = window_is_silent[i]

        if e1 and not e2:
            speaking_start = i * window_size

        if not e1 and e2:
            speaking_end = i * window_size
            new_speaking_interval = [speaking_start - ease_in, speaking_end + ease_in]
            need_to_merge = len(speaking_intervals) > 0 and speaking_intervals[-1][1] > new_speaking_interval[0]
            if need_to_merge:
                merged_interval = [speaking_intervals[-1][0], new_speaking_interval[1]]
                speaking_intervals[-1] = merged_interval
            else:
                speaking_intervals.append(new_speaking_interval)

    return speaking_intervals


def main():
    # Parse args
    # Input file path
    file_in = sys.argv[1]
    # Output file path
    file_out = sys.argv[2]

    vid = VideoFileClip(file_in)
    intervals_to_keep = find_speaking(vid.audio)

    print("Intervales a decouper :" + str(intervals_to_keep))
    
    keep_clips = [vid.subclip(start, end) for [start, end] in intervals_to_keep]

    edited_video = concatenate_videoclips(keep_clips)
    edited_video.write_videofile(file_out,
        fps=60,
        preset='ultrafast',
        codec='libx264',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True,
        audio_codec="aac",
        threads=6
    )

    vid.close()

if __name__ == '__main__':
    main()
