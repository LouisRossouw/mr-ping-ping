
import os
import sys
from time import sleep

this_dir = os.path.dirname(__file__)
root_dir = os.path.dirname(this_dir)

sys.path.append(this_dir)

import utils  # nopep8


def save_data(name, dir, stats):
    """ saves data. """

    current_date = utils.get_dates_new()

    date_year = current_date["date_year"]
    date_now_full = current_date["date_now_full"]
    day_month_name = current_date["day_month_name"]

    data_dir = os.path.join(f"{root_dir}", "data")
    pings_dir = os.path.join(f"{root_dir}", "data", dir)

    if name:
        data_log_dir = os.path.join(pings_dir, str(name))
    else:
        data_log_dir = pings_dir

    utils.check_path_exists(data_dir)
    utils.check_path_exists(pings_dir)
    utils.check_path_exists(data_log_dir)

    current_data_list = os.listdir(data_log_dir)
    data_count = len(current_data_list)

    json_name = f"{str(data_count)}_{str(date_year)}_{day_month_name}.json"
    file_path = os.path.join(data_log_dir, json_name)

    # Json file.
    if os.path.exists(file_path) != True:
        data_count = len(current_data_list) + 1
        json_name = f"{str(data_count)}_{str(date_year)}_{day_month_name}.json"
        file_path = os.path.join(data_log_dir, json_name)
        utils.write_to_json(file_path, {})
        sleep(2)

    current = utils.read_json(file_path)
    current[str(date_now_full)] = stats

    utils.write_to_json(file_path, current)
    sleep(2)


if __name__ == "__main__":
    print('testing')
