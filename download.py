# coding: utf-8

import requests, os
import threading
import codecs
import time
import argparse


class TaskManager(object):
    def __init__(self, video_list, num_threads=10, limit=None):
        self.video_list = video_list
        self.num_threads = num_threads
        self._limit = limit

    def create_task(self):
        tasks = []
        for video_url in codecs.open(self.video_list, "r", "utf-8"):
            video_url = video_url.strip()
            if not video_url:
                continue
            tasks.append(video_url)
        return tasks

    def create_split_tasks(self):
        tasks = self._split_tasks(self.create_task(), self.num_threads)
        if self._limit is not None:
            tasks = tasks[: self._limit]
        return tasks

    def _split_tasks(self, tasks, splits):
        total_length = len(tasks)
        num_splits = min(total_length, splits)
        split_tasks = [[] for _ in range(num_splits)]
        for i in range(total_length):
            bin_num = i % num_splits
            split_tasks[bin_num].append(tasks[i])
        return split_tasks


class Saver(object):
    def __init__(self, res_dir):
        self._res_dir = res_dir
        if not os.path.exists(self._res_dir):
            os.makedirs(self._res_dir)

    def dump(self, ret):
        video_name, video_file = ret
        with open(self.get_save_path(video_name), "wb") as writer:
            writer.write(video_file)
        print(f"downloaded:{video_name}")

    def get_save_path(self, video_name):
        return os.path.join(self._res_dir, video_name)

    def query_exist(self, video_name):
        save_path = self.get_save_path(video_name)
        if os.path.exists(save_path):
            return True
        return False


class RequestThread(threading.Thread):
    def __init__(
        self, saver, tasklist, user_name, password, interval=0.1, *args, **kwargs
    ):
        self.saver = saver
        self.tasklist = tasklist
        self.interval = interval
        self.user_name = user_name
        self.password = password
        super(RequestThread, self).__init__(*args, **kwargs)

    def run(self):
        for video_url in self.tasklist:
            video_name = video_url.split("/")[-1]
            if self.saver.query_exist(video_name):
                continue
            try:
                ret = self.request(video_url)
                self.saver.dump((video_name, ret))
            except:
                continue
            time.sleep(self.interval)

    def request(self, video_url):
        r = requests.get(video_url, auth=(self.user_name, self.password))
        return r.content


def parse_args():
    parser = argparse.ArgumentParser()

    # Data path
    parser.add_argument(
        "--video_list_file", type=str, help="path to howto100m_videos.txt"
    )
    parser.add_argument(
        "--save_dir",
        default="videos",
        type=str,
        help="The directory to save video files.",
    )
    parser.add_argument(
        "--num_threads", default=20, type=int, help="The number of threads to download"
    )

    # Auth info
    parser.add_argument(
        "--user_name", type=str, help="User name provided by Howto100M dataset owners."
    )
    parser.add_argument(
        "--password", type=str, help="Password provided by Howto100M dataset owners."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    saver = Saver(args.save_dir)
    tasks = TaskManager(
        args.video_list_file, num_threads=args.num_threads
    ).create_split_tasks()

    threads = [
        RequestThread(saver, subtask, args.user_name, args.password)
        for subtask in tasks
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
