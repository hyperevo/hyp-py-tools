import csv
import json
import os
from typing import (
    List,
    Any
)


def load_from_csv(file:str, num_lines_for_header:int=0, delimiter = ',') -> List[Any]:
    csv_array = []
    with open(file, 'rt') as csvfile:
        csv_data = csv.reader(csvfile, delimiter=delimiter, quotechar='|')

        count = 0
        for row in csv_data:
            if count >= num_lines_for_header:
                new_row = []
                for i in row:
                    try:
                        new_row.append(float(i))
                    except ValueError:
                        new_row.append(i)
                csv_array.append(new_row)
            count += 1
    return csv_array


def load_from_JSON(file):
    if os.path.isfile(file) == False:
        return False
    with open(file, 'rt') as json_data:
        d = json.load(json_data)
        json_data.close()
        return d['train_input'], d['train_expected_output']


def load_from_general_JSON(file):
    if os.path.isfile(file) == False:
        return False
    with open(file, 'rt') as json_data:
        d = json.load(json_data)
        json_data.close()
        return d


def save_to_general_JSON(file, data):
    # make directory if it doesnt exist
    # get directory
    directory = os.path.dirname(file)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(file, 'w') as outfile:
        json.dump(data, outfile)
        outfile.close()