import json
import re
from collections import Counter
from datetime import datetime


def json_load():
    json_string = input()
    return json.loads(json_string)


class BusData:
    def __init__(self, json_objects):
        self.json_objects = json_objects
        self.transfer_stops_set = None

    # Step 2/6
    def name_type_time_fixer(self):
        stop_name_errors = 0
        stop_type_errors = 0
        a_time_errors = 0

        # patterns
        stop_name_pattern = re.compile('[A-Z][a-z]* ([A-Z][a-z]*)* ?(Road|Avenue|Boulevard|Street)')
        stop_type_pattern = re.compile(r'\b[SOF]\b|^$')
        a_time_pattern = re.compile(r"\b(?:0[0-9]|1[0-9]|2[0-3]):[0-5]\d\b")
        for dict_obj in self.json_objects:
            for key in dict_obj:
                value = dict_obj[key]

                # Stop name: Name of current stop, Type: String, Format: [name] [suffix]
                if key == "stop_name":
                    if isinstance(value, str):
                        if not stop_name_pattern.fullmatch(value):
                            stop_name_errors += 1
                            continue
                    else:
                        stop_name_errors += 1
                        continue
                    print(value)

                # Stop type: Character, Format: S or O or F
                elif key == "stop_type":
                    if isinstance(value, str):
                        if not stop_type_pattern.match(value):
                            stop_type_errors += 1
                    else:
                        stop_type_errors += 1

                # Arrival time: String, Format: 24 hour date, HH:MM
                elif key == "a_time":
                    if len(value) != 5:
                        a_time_errors += 1
                    elif isinstance(value, str):
                        if not a_time_pattern.match(value):
                            a_time_errors += 1
                    else:
                        a_time_errors += 1

        print(f"Format validation: {stop_name_errors + stop_type_errors + a_time_errors} errors")
        print(f"stop_name: {stop_name_errors}")
        print(f"stop_type: {stop_type_errors}")
        print(f"a_time: {a_time_errors}")

    # Step 3/6
    def count_bus_stops(self):
        bus_count_counter = Counter()
        for dict_obj in self.json_objects:
            for key in dict_obj:
                value = str(dict_obj[key])
                if key == "bus_id":
                    if value in bus_count_counter:
                        bus_count_counter[value] += 1
                    else:
                        bus_count_counter[value] = 1
        print("Line names and number of stops:")
        for bus_item in bus_count_counter.items():
            print(f"bus_id: {bus_item[0]}, stops: {bus_item[1]}")

    # Step 4/6
    def get_bus_dict(self):
        bus_dict = {}
        for dict_obj in self.json_objects:
            for key in dict_obj:
                if key == "bus_id":
                    id_number = str(dict_obj[key])
                    if id_number not in bus_dict.keys():
                        bus_dict[id_number] = []
                if key == "stop_name":
                    stop_name = dict_obj[key]
                if key == "stop_type":
                    stop_type = dict_obj[key]
                    bus_dict[id_number].append((stop_type, stop_name))
        for bus in bus_dict:
            if not bus_dict[bus][0][0] == "S":
                # print(f"There is no start or end stop for the line: {bus}.")
                # exit()
                pass
            if not bus_dict[bus][-1][0] == "F":
                # print(f"There is no start or end stop for the line: {bus}.")
                # exit()
                pass
        start_stops = set()
        transfer_stops = set()
        finish_stops = set()
        transfer_stops_counter = Counter()
        finish_stops_counter = Counter()
        for bus_number in bus_dict:
            for stop in bus_dict[bus_number]:
                if stop[0] == "S":
                    start_stops.add(stop[1])
                if stop[0] == "F":
                    finish_stops.add(stop[1])
                    finish_stops_counter[stop[1]] += 1

        for bus_number in bus_dict:
            for stop in bus_dict[bus_number]:
                if stop[0] == "O" or stop[0] == "":
                    if stop[1] in start_stops or stop[1] in transfer_stops or stop[1] in finish_stops:
                        transfer_stops.add(stop[1])
                    else:
                        transfer_stops_counter[stop[1]] += 1

        for item in transfer_stops_counter.items():
            if item[1] > 1:
                transfer_stops.add(item[0])
        for item in finish_stops_counter.items():

            if item[1] > 1:
                transfer_stops.add(item[0])
        # print(f"Start stops: {len(start_stops)} {sorted(start_stops)}")
        # print(f"Transfer stops: {len(transfer_stops)} {sorted(transfer_stops)}")
        # print(f"Finish stops: {len(finish_stops)} {sorted(finish_stops)}")
        self.transfer_stops_set = transfer_stops

    # Step 5/6
    # time (a_time) , bus_line (bus_id), stop_name
    def time_check(self):
        fail_string = []
        skip_bus_line = []
        for index, stop_1 in enumerate(self.json_objects):
            if stop_1["bus_id"] not in skip_bus_line:
                current_bus_line = stop_1["bus_id"]
                current_time = stop_1["a_time"]
                current_time = datetime.strptime(current_time, "%H:%M").time()
                counter = 0
                if index < len(self.json_objects) - 1:
                    stop_2 = self.json_objects[index + 1]
                    if counter == 0:
                        counter += 1
                        if current_bus_line == stop_2["bus_id"]:
                            new_time = stop_2["a_time"]
                            new_time = datetime.strptime(new_time, "%H:%M").time()
                            if new_time <= current_time:
                                fail_string.append(
                                    f"bus_id line {current_bus_line}: wrong time on station {stop_2['stop_name']}")
                                skip_bus_line.append(current_bus_line)
        if fail_string:
            print("Arrival time test:")
            for fail in fail_string:
                print(fail)
        else:
            print("OK")

    # Step 6/6
    def check_on_demand(self):
        wrong_stop_type = []
        transfer_stops = self.transfer_stops_set
        on_demand_stops = []
        for dict_obj in self.json_objects:
            if dict_obj["stop_type"] == "O":
                if dict_obj["stop_name"] in transfer_stops:
                    wrong_stop_type.append(dict_obj["stop_name"])
        if wrong_stop_type:
            print("On demand stops test:")
            print(f"Wrong stop type: {sorted(wrong_stop_type)}")
        else:
            print("OK")

def main():
    json_objects = json_load()
    bus_data = BusData(json_objects)
    bus_data.get_bus_dict()
    bus_data.check_on_demand()


if __name__ == "__main__":
    main()
