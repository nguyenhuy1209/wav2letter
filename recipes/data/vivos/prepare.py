from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import os
import sox

import numpy
# from tqdm import tqdm
# from utils import find_transcript_files, transcript_to_list

LOG_STR = " To regenerate this file, please, remove it."

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="VIVOS Dataset creation.")
    parser.add_argument(
        "--dst",
        help="destination directory where to store data",
        default="./vivos",
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
    data_http = "https://ailab.hcmus.edu.vn/assets/vivos.tar.gz"

    # Download the audio data
    print("Downloading the VIVOS data.", flush=True)
    if not os.path.exists(os.path.join(audio_path, "vivos")):
        print("Downloading and unpacking")
        cmd = """wget -c {http} -P {path};
                    yes n 2>/dev/null | gunzip {path}/vivos.tar.gz;
                    tar -C {path} -xf {path}/vivos.tar"""
        os.system(cmd.format(path=audio_path, http=data_http))
    else:
        log_str = "Data exists, skip its downloading and unpacking."
        print(log_str + LOG_STR, flush=True)

    # Prepare the audio data
    print("Converting audio data into necessary format.", flush=True)
    for ds_type in ['train', 'test']:
        src = os.path.join(audio_path, "vivos", ds_type)
        assert os.path.exists(src), "Unable to find the directory - '{src}'".format(
            src=src
        )
        dst_list = os.path.join(lists_path, ds_type + ".lst")
        if os.path.exists(dst_list):
            print(
                "Path {} exists, skip its generation.".format(dst_list) + LOG_STR,
                flush=True,
            )
            continue

        print("Writing to {dst}...".format(dst=dst_list), flush=True)
        filename = os.path.join(src, "prompts.txt")
        with open(filename, encoding="utf-8") as f:
            lines = f.readlines()
        path = os.path.join(src, "waves")
        with open(os.path.join(dst_list), 'w', encoding="utf-8") as f:
            for line in lines:
                index = line.find(" ")
                name, transcript = line[:index], line[index+1:]
                spk = name.split("_")[0]
                wav_path = os.path.join(path, spk, name + ".wav")
                duration = sox.file_info.duration(wav_path) * 1000
                f.write("{} {} {} {}".format(name, wav_path, duration, transcript))

    # Split train set to train+dev set
    train_lst_path = os.path.join(lists_path, 'train' + ".lst")
    train2_lst_path = os.path.join(lists_path, 'train2' + ".lst")
    dev_lst_path = os.path.join(lists_path, 'dev' + ".lst")
    if not os.path.exists(dev_lst_path):
        cmd = f"""head -n {args.ndev_utt} {train_lst_path} > {dev_lst_path} ; \
                echo "$(tail -n +{args.ndev_utt+1} {train_lst_path})" > {train_lst_path}"""
        print("Writing to {dst}...".format(dst=dev_lst_path), flush=True)
        os.system(cmd)
    else:
        print(
            "Path {} exists, skip its generation.".format(dev_lst_path) + LOG_STR,
            flush=True,
        )

    # Prepare text data
    for ds_type in ['train', 'dev', 'test']:
        current_path = os.path.join(text_path, ds_type + ".txt")
        if not os.path.exists(current_path):
            with open(os.path.join(lists_path, ds_type + ".lst"), "r", encoding="utf-8") as flist, open(
                os.path.join(text_path, ds_type + ".txt"), "w", encoding="utf-8"
            ) as fout:
                for line in flist:
                    fout.write(" ".join(line.strip().split(" ")[3:]) + "\n")
        else:
            print(
                "Path {} exists, skip its generation.".format(current_path) + LOG_STR,
                flush=True,
            )

    print("Done!", flush=True)