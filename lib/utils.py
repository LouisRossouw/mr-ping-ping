
import os
import sys
from time import sleep
import settings

SETTINGS = settings.Settings()
sys.path.append(SETTINGS.root_dir)

import test as utils  # nopep8

root_dir = SETTINGS.root_dir


def save_data(account_name, stats):
    """ saves data. """

    print("Formatting and saving data")

    current_date = utils.get_dates()

    data_log_dir = os.path.join(
        f"{root_dir}", "data", "instagram", str(account_name))

    # Data dir.
    if os.path.exists(data_log_dir) != True:
        os.mkdir(data_log_dir)
        sleep(2)

    current_data_list = os.listdir(data_log_dir)
    data_count = len(current_data_list)
    json_name = f"{str(data_count)}_{str(current_date[4])}_{current_date[6]}.json"
    file_path = os.path.join(data_log_dir, json_name)

    # Json file.
    if os.path.exists(file_path) != True:
        data_count = len(current_data_list) + 1
        json_name = f"{str(data_count)}_{str(current_date[4])}_{current_date[6]}.json"
        file_path = os.path.join(data_log_dir, json_name)
        utils.write_to_json(file_path, {})
        sleep(2)

    current = utils.read_json(file_path)
    current[current_date[8]] = {
        "name": account_name,
        "stats": stats
    }

    utils.write_to_json(file_path, current)
    sleep(2)


if __name__ == "__main__":
    print('testing')
