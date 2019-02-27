import os
import csv
import sys
import re
import numpy as np

def read_beat_annotation(path_annotation_full):
    _, file_extension = os.path.splitext(path_annotation_full)
    if file_extension == ".csv":
        sep = ','
    elif file_extension == ".beats":
        sep = ' '
    else:
        sep = ' '
    with open(path_annotation_full, mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=sep, quotechar='|')
        try:
            beats = []
            counts = []
            for row in reader:
                if len(row) == 3 and row[0] and not row[1] and row[2]:
                    row = list(row[i] for i in [0, 2])
                elif len(row) != 2:
                    row = row[0].split()

                if len(row) != 2:
                    raise IOError("Ill-formed annotation: " + path_annotation_full)

                try:
                    b = string2number(row[0])
                    beats.append(b)
                    beat_count_string = row[1]
                    # Hack to reformat annotations like "11.1" which means beat 1 in measure 11
                    if beat_count_string.__contains__("."):
                        beat_count_string = beat_count_string.split(".")[1]
                    c = int(string2number(beat_count_string))
                    counts.append(c)
                except ValueError as e:
                    raise ValueError("could not parse row:" + str(row) + " of annotation " + paths.rel_path(path_annotation_full))

        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(path_annotation_full, reader.line_num, e))
    anno_beat_times = np.array(beats)
    anno_beat_counts = np.array(counts)
    return anno_beat_counts, anno_beat_times

def string2number(str):
    return float(re.sub("[^0-9\.]", "", str))

def write_beat_annotation(beat_counts, beat_times, path_csv):
    # check python version
    PY3 = sys.version_info[0] == 3
    # write output to csv file
    if PY3:
        with open(path_csv, "w", newline='', encoding="utf8") as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar="'")
            for i in range(len(beat_times)):
                writer.writerow([beat_times[i]] + ['"' + str(beat_counts[i]) + '"'])
    else:
        with open(path_csv, "w") as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar="'", lineterminator='\n')
            for i in range(len(beat_times)):
                writer.writerow([beat_times[i]] + ['"' + str(beat_counts[i]) + '"'])