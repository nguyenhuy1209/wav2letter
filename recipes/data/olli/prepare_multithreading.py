from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import os
import sox
import threading

LOG_STR = " To regenerate this file, please, remove it."

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="OLLI Dataset preparation.")
    parser.add_argument(
        "--dst",
        help="destination directory where to store data",
        default="./olli",
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
        default=4572,
        type=int,
    )

    args = parser.parse_args()

    data_path = '/olli_data/thuc_kaldi_format_data/'
    text_path = os.path.join(args.dst, "text")
    lists_path = os.path.join(args.dst, "lists")
    os.makedirs(text_path, exist_ok=True)
    os.makedirs(lists_path, exist_ok=True)
    
    # Prepare the audio data
    print("Converting audio data into necessary format.", flush=True)
    for ds_type in ['train', 'test']:
        dst_list = os.path.join(lists_path, ds_type + ".lst")
        if os.path.exists(dst_list):
            print(
                "Path {} exists, skip its generation.".format(dst_list) + LOG_STR,
                flush=True,
            )
            continue

        print("Writing to {dst}...".format(dst=dst_list), flush=True)
        text_file = os.path.join(data_path, ds_type, "text")
        path_file = os.path.join(data_path, ds_type, "wav.scp")
        path_dict = {}
        with open(text_file, encoding="utf-8") as f:
            text_lines = f.readlines()
        with open(path_file, encoding="utf-8") as f:
            for line in f:
                utt_id, path = line.split(" ")
                path_dict[utt_id] = path
        
        num_threads = 7
        num_lines = len(text_lines)
        num_lines_per_threads = int(num_lines / num_threads)

        def create_lst_file(thread_index):
            with open(os.path.join(lists_path, f'output_{thread_index}_{ds_type}'), 'w', encoding="utf-8") as f:
                if thread_index == num_threads - 1:
                    for t_line in text_lines[thread_index*num_lines_per_threads:]:
                        wav_path = None
                        duration = None
                        index = t_line.find(" ")
                        utt_id, transcript = t_line[:index], t_line[index+1:]
                        wav_path = path_dict[utt_id][:-1]
                        duration = sox.file_info.duration(wav_path) * 1000
                        f.write("{} {} {} {}".format(utt_id, wav_path, duration, transcript))
                else:
                    for t_line in text_lines[thread_index*num_lines_per_threads: \
                                            thread_index*num_lines_per_threads+num_lines_per_threads]:
                        wav_path = None
                        duration = None
                        index = t_line.find(" ")
                        utt_id, transcript = t_line[:index], t_line[index+1:]
                        wav_path = path_dict[utt_id][:-1]
                        duration = sox.file_info.duration(wav_path) * 1000
                        f.write("{} {} {} {}".format(utt_id, wav_path, duration, transcript))
                print(f"Thread {thread_index} finished!")

        thread_list = list()
        for i in range(num_threads):
            thread = threading.Thread(target=create_lst_file, args=(i,))
            thread_list.append(thread)
            thread.start()
        for thread in thread_list:
            thread.join()

        with open(os.path.join(dst_list), 'w', encoding="utf-8") as f:
            for i in range(num_threads):
                f.write(open(f"output_{i}_{ds_type}", "r", encoding="utf-8").read())

    # Split train set to train+dev set
    train_lst_path = os.path.join(lists_path, 'train' + ".lst")
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