import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from typing import List, Mapping

import numpy as np
import pandas as pd


def str2time(time_str: str) -> datetime.time:
    _time = datetime.strptime(time_str, "%H:%M:%S").time()
    return _time


def str2date(date_str: str) -> datetime.date:
    _date = datetime.strptime(date_str, "%Y%m%d").date()
    return _date


def str2datetime(date_str: str, time_str: str) -> datetime:
    _time = str2time(time_str)
    _date = str2date(date_str)
    _datetime = datetime.combine(date=_date, time=_time)
    return _datetime


def load_json(filepath: str) -> dict:
    with open(filepath) as f:
        content = json.load(f)
    return content


def get_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("dmon_output", help="path to nvidia-smi dmon output")
    args = p.parse_args()
    return args


def read_lines(filepath: str) -> List[str]:
    with open(filepath) as f:
        lines = f.readlines()
    return lines


def extract_metric_line(filepath: str) -> str:
    lines = read_lines(filepath)

    for idx in range(len(lines) - 1):
        if lines[idx][0] == "#" and lines[idx + 1][0] == "#":
            metric_line = lines[idx]
            return metric_line
    else:
        return ""


@dataclass
class DataPoint:
    gpuId: int
    name: str
    value: int


@dataclass
class DataPointWithTime(DataPoint):
    time: datetime.time


@dataclass
class DataPointWithDate(DataPoint):
    date: datetime.date


@dataclass
class DataPointWithDateTime(DataPoint):
    date: datetime.date
    time: datetime.time


def get_all_metrics(metric_line: str, file_path: str) -> Mapping[str, List[DataPoint]]:
    metric_str_list = metric_line.split()
    first_elem = metric_str_list[0]
    second_elem = metric_str_list[1]

    lines = read_lines(file_path)
    datapoints = dict()

    if first_elem == "#" and second_elem == "gpu":
        # see docs/example_dmon.txt for an example
        metrics = metric_str_list[1:]
        datapoints = {m: [] for m in metrics}
        for line in lines:
            if line[0] == "#":
                continue
            else:
                data = line.split()
                for m, d in zip(metrics, data):
                    if d == "-":
                        datapoints[m].append(np.nan)
                    else:
                        datapoints[m].append(int(d))

    elif first_elem == "#Time" and second_elem == "gpu":
        # see docs/example_dmon_time.txt for an example
        metrics = metric_str_list[2:]

    elif first_elem == "#Date" and second_elem == "gpu":
        # see docs/example_dmon_date.txt for an example
        metrics = metric_str_list[2:]
    elif first_elem == "#Date" and second_elem == "Time":
        # see docs/example_dmon_datetime.txt for an example
        metrics = metric_str_list[3:]
    else:
        pass

    return datapoints


if __name__ == "__main__":
    _METRICS_JSON = "./metrics.json"
    # metrics_dict = load_json(_METRICS_JSON)

    args = get_args()
    metric_line = extract_metric_line(args.dmon_output)
    stats_dict = get_all_metrics(metric_line=metric_line, file_path=args.dmon_output)

    df = pd.DataFrame(data=stats_dict, dtype=pd.Int64Dtype())
