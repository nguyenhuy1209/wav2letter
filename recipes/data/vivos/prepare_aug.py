from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import os
import sox

import numpy
import random
# from tqdm import tqdm
# from utils import find_transcript_files, transcript_to_list

LOG_STR = " To regenerate this file, please, remove it."

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="VIVOS Dataset creation.")
    parser.add_argument(
        "--dst",
        help="destination directory where to store data",
        default="./vivos_aug",
    )
    parser.add_argument(
        "-p",
        "--process",
        help="number of process for multiprocessing",
        default=8,
        type=int,
    )
    parser.add_argument(
        "--ndev_utt",
        help="number of validation set utterances",
        default=760,
        type=int,
    )

    args = parser.parse_args()

    audio_path = os.path.join(args.dst, "audio")
    text_path = os.path.join(args.dst, "text")
    lists_path = os.path.join(args.dst, "lists")
    os.makedirs(audio_path, exist_ok=True)
    os.makedirs(text_path, exist_ok=True)
    os.makedirs(lists_path, exist_ok=True)
    
    # Extract the audio data
    print("Unpacking the VIVOS augmented data.", flush=True)
    if not os.path.exists(os.path.join(audio_path, "vivos_auged")):
        print("Unpacking")
        cmd = """yes n 2>/dev/null | gunzip {path}/vivos_auged.tar.gz;
                    tar -C {path} -xf {path}/vivos_auged.tar"""
        os.system(cmd.format(path=audio_path))
    else:
        log_str = "Data exists, skip its unpacking."
        print(log_str + LOG_STR, flush=True)

    # Prepare the audio data
    print("Converting audio data into necessary format.", flush=True)
    for ds_type in ['train', 'test']:
        src_list = [os.path.join(audio_path, o) for o in os.listdir(audio_path) if os.path.isdir(os.path.join(audio_path, o))]
        for src in src_list:
            _, ps, sp, _ = src.split('/')[-1].split('_')
            ps = ps[2:]
            sp = sp[2:]
            meta = f"PS{ps}SP{sp}"

            src = os.path.join(src, ds_type)
            dst_list = os.path.join(lists_path, ds_type + ".lst")

            print("Writing to {dst}...".format(dst=dst_list), flush=True)
            filename = os.path.join(audio_path, f"prompts_{ds_type}.txt")
            with open(filename, encoding="utf-8") as f:
                lines = f.readlines()
                if ds_type == "train":
                    random.shuffle(lines)
                    lines_dev, lines = lines[:760], lines[760:]
            path = os.path.join(src, "waves")
            with open(os.path.join(dst_list), 'a', encoding="utf-8") as f:
                for line in lines:
                    index = line.find(" ")
                    name, transcript = line[:index], line[index+1:]
                    name = name + meta
                    spk = name.split("_")[0]
                    wav_path = os.path.join(path, spk, name + ".wav")
                    duration = sox.file_info.duration(wav_path) * 1000
                    f.write("{} {} {} {}".format(name, wav_path, duration, transcript))

            if ds_type == "train":
                print("Writing to {dst}...".format(dst=os.path.join(lists_path, "dev" + ".lst")), flush=True)
                with open(os.path.join(os.path.join(lists_path, "dev" + ".lst")), 'a', encoding="utf-8") as f:
                    for line in lines_dev:
                        index = line.find(" ")
                        name, transcript = line[:index], line[index+1:]
                        name = name + meta
                        spk = name.split("_")[0]
                        wav_path = os.path.join(path, spk, name + ".wav")
                        duration = sox.file_info.duration(wav_path) * 1000
                        f.write("{} {} {} {}".format(name, wav_path, duration, transcript))

    # Prepare text data
    for ds_type in ['train', 'dev', 'test']:
        current_path = os.path.join(text_path, ds_type + ".txt")
        if not os.path.exists(current_path):
            with open(os.path.join(lists_path, ds_type + ".lst"), "r", encoding="utf-8") as flist, open(
                os.path.join(text_path, ds_type + ".txt"), "w", encoding="utf-8"
            ) as fout:
                flist = list(map(lambda line: " ".join(line.strip().split(" ")[3:]), flist))
                flist = list(set(flist))
                for line in flist:
                    fout.write(line + "\n")
        else:
            print(
                "Path {} exists, skip its generation.".format(current_path) + LOG_STR,
                flush=True,
            )

    print("Done!", flush=True)
