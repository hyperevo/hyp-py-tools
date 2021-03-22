from sortedcontainers import SortedDict, SortedSet, SortedList
import numpy as np

from hyp_py_tools.exceptions import InvalidTimestampsInDataError, NotEnoughInputData


class SparseTimeSeriesDataSet:
    # A dataset designed for dealing with sparse time series data that needs to be kept in sync in time.
    def __init__(self, unique_timestamps = None, minimum_time_between_timestamps = None, mode='strict'):
        # possible modes are strict, remove_difference, union
        if unique_timestamps is not None:
            self.unique_timestamps = SortedSet(unique_timestamps)
        else:
            self.unique_timestamps = SortedSet()

        self.mode = mode
        self.all_raw_data = {}

        #dict of sorteddicts
        self.timestamp_indexed_data = {}

        self.minimum_time_between_timestamps = minimum_time_between_timestamps
        self.check_minimum_timestamp_interval()


    def __len__(self):
        return len(self.unique_timestamps)

    @classmethod
    def sample_data_at_intervals(cls, start_timestamp, end_timestamp, interval, data):
        # extends previous datapoint if one is missing
        timestamps = SortedList([x[0] for x in data])

        start_timestamp = int(start_timestamp)
        end_timestamp = int(end_timestamp)

        assert(timestamps[0] <= start_timestamp)
        assert(timestamps[-1] >= end_timestamp)
        sampled_data = []

        for timestamp in range(start_timestamp, end_timestamp+1, interval):
            index = timestamps.bisect_right(timestamp)-1
            new_datapoint = data[index].copy()
            new_datapoint[0] = timestamp
            sampled_data.append(new_datapoint)

        return sampled_data

    @property
    def ids(self):
        return list(self.all_raw_data.keys())

    @property
    def first_timestamp(self):
        return self.unique_timestamps[0]

    def first_timestamp_for_id(self, id):
        return self.all_raw_data[id][0][0]

    @property
    def last_timestamp(self):
        return self.unique_timestamps[-1]

    def last_timestamp_for_id(self, id):
        return self.all_raw_data[id][-1][0]

    def first_unpadded_index_for_id(self, id):
        first_timestamp = self.first_timestamp_for_id(id)
        return self.unique_timestamps.index(first_timestamp)

    def last_unpadded_index_for_id(self, id):
        last_timestamp = self.last_timestamp_for_id(id)
        return self.unique_timestamps.index(last_timestamp)


    def check_minimum_timestamp_interval(self):
        if self.minimum_time_between_timestamps is not None:
            prev_timestamp = 0
            for timestamp in self.unique_timestamps:
                if timestamp-prev_timestamp < self.minimum_time_between_timestamps:
                    raise InvalidTimestampsInDataError("Found timestamps that have less than the required {} between them".format(self.minimum_time_between_timestamps))
                prev_timestamp = timestamp

    def add(self, id: str, data):
        if len(data) == 0:
            raise ValueError("Tried to add empty data for id {}".format(id))

        if id in self.all_raw_data and self.all_raw_data[id] == data:
            print("Data for id {} already added.".format(id))
            return

        self.all_raw_data[id] = data

        if len(data[0]) > 2:
            # we have multidimensional data
            timestamp_indexed_data = SortedDict([[int(x[0]), x[1:]] for x in data])
        else:
            timestamp_indexed_data = SortedDict([[int(x[0]), x[1]] for x in data])


        new_timestamps = {x[0] for x in data}
        difference = new_timestamps.difference(self.unique_timestamps)

        if self.mode == 'strict':
            if len(difference) != 0:
                raise InvalidTimestampsInDataError("Tried to add new data with id {} that includes timestamps that are not in the set of allowed timestamps. "
                                                   "Difference = {}".format(id, difference))
            opposite_difference = self.unique_timestamps.difference(new_timestamps)
            # for timestamp_current in opposite_difference:
            #     if timestamp_current > min(new_timestamps) and timestamp_current < max(new_timestamps):
            #         raise Exception("Missing timestamps in the middle of the data")

        elif self.mode == 'remove_difference':
            for timestamp_to_remove in difference:
                del(timestamp_indexed_data[timestamp_to_remove])

        elif self.mode == 'union':
            self.unique_timestamps = self.unique_timestamps.union(new_timestamps)

        self.check_minimum_timestamp_interval()

        if len(timestamp_indexed_data) == 0:
            raise NotEnoughInputData("The data being added has zero length. If the mode is remove_difference, then this means that the new data has no timestamps in common with the required timestamps")

        self.timestamp_indexed_data[id] = timestamp_indexed_data


    def get_left_and_right_padding_required(self, ids):
        padding_required = []
        for id in ids:
            first_timestamp_for_id = self.first_timestamp_for_id(id)
            last_timestamp_for_id = self.last_timestamp_for_id(id)
            left_padding = self.unique_timestamps.index(first_timestamp_for_id)
            right_padding = len(self) - self.unique_timestamps.index(last_timestamp_for_id)-1

            assert(self.all_raw_data[id][0][0] == self.unique_timestamps[left_padding])
            assert(self.all_raw_data[id][-1][0] == self.unique_timestamps[-(right_padding+1)])

            padding_required.append([left_padding, right_padding])
        return padding_required

    def get_data_extend_missing_internal(self, id: str):
        # This function does't pad the left or right of the data, but it will fill in any missing data
        # using the previous value
        timestamp_indexed_data = self.timestamp_indexed_data[id]

        timestamps_in_this_data = set(timestamp_indexed_data.keys())
        missing_timestamps = self.unique_timestamps - timestamps_in_this_data

        if len(missing_timestamps) > 0:
            for timestamp in missing_timestamps:
                entry_index = timestamp_indexed_data.bisect_right(timestamp)

                if entry_index != 0 and entry_index < len(timestamp_indexed_data):
                    # only pad in the middle of the data and not at the end
                    current_padded_value = timestamp_indexed_data.peekitem(entry_index - 1)[1]
                    timestamp_indexed_data[timestamp] = current_padded_value

        if isinstance(timestamp_indexed_data.peekitem(0)[1], list) or isinstance(timestamp_indexed_data.peekitem(0)[1], tuple):
            to_return = [[x[0], *x[1]]for x in timestamp_indexed_data.items()]
        else:
            to_return = list(timestamp_indexed_data.items())
        return to_return


    def get_padded_data_in_sync(self, padding_val = "extend"):
        # It will always pad missing values in the middle or end of the data by extending the previous value.
        # The padding_val variable determined how to pad the beginning when there is no value before it.
        padded_timestamp_indexed_data = {}

        for ric, timestamp_indexed_data in self.timestamp_indexed_data.items():
            padded_timestamp_indexed_data[ric] = timestamp_indexed_data

            timestamps_in_this_data = set(timestamp_indexed_data.keys())
            missing_timestamps = self.unique_timestamps - timestamps_in_this_data

            if len(missing_timestamps) > 0:
                for timestamp in missing_timestamps:
                    entry_index = padded_timestamp_indexed_data[ric].bisect_right(timestamp)
                    if entry_index == 0:
                        if padding_val == 'extend':
                            current_padded_value = padded_timestamp_indexed_data[ric].peekitem(entry_index)[1]
                        else:
                            current_padded_value = padding_val
                    else:
                        current_padded_value = padded_timestamp_indexed_data[ric].peekitem(entry_index-1)[1]

                    padded_timestamp_indexed_data[ric][timestamp] = current_padded_value

        return padded_timestamp_indexed_data


    def get_start_and_end_index_for_concat_data(self, keys):
        start_stop = []
        current_position = 0
        for id in keys:
            if id in self.timestamp_indexed_data:
                length_of_data = len(self.timestamp_indexed_data[id])
                start_stop.append([current_position,current_position+length_of_data])
                current_position = length_of_data
            else:
                print("warning: tried to concat data for keys {} but key {} is missing".format(keys, id))

        return start_stop


    def concat_data_unpadded(self, keys, as_numpy = True, with_timestamps = True):
        data_to_concat = []
        for id in keys:
            if id in self.timestamp_indexed_data:
                if with_timestamps:
                    data_to_concat.append(np.squeeze(self.timestamp_indexed_data[id].items()[:]))
                else:
                    data_to_concat.append(np.squeeze(self.timestamp_indexed_data[id].values()[:]))
            else:
                print("warning: tried to concat data for keys {} but key {} is missing".format(keys, id))


        if as_numpy:
            return np.concatenate(data_to_concat)
        else:
            return np.concatenate(data_to_concat).tolist()









if __name__ == "__main__":
    # dataset = SparseTimeSeriesDataSet()
    # test = [['a',1],['d',2],['c',3]]
    # dataset.add('set_1', test)
    # test2 = [['a', 1], ['e', 2], ['c', 3], ['b', 1.5]]
    # dataset.add('set_2', test2)
    # print(dataset.get_padded_data_in_sync())

    # test1 = SortedSet([1,2,3,4,5])
    # test2 = SortedSet([2,3,4])
    # print(test2.difference(test1))

    test_data = [[1,'a'],[2,'b'],[4,'c'],[8,'d']]
    sampled_dataset = SparseTimeSeriesDataSet.sample_data_at_intervals(1, 8, 1,test_data)
    print(test_data)
    print(sampled_dataset)






