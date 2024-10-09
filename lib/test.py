import os
import time
import json
import random
import datetime
import calendar
import shutil
import subprocess
from pathlib import Path
from datetime import timedelta
import requests
import string

from colorama import Fore, Back, Style, init


def remove_ext(files_path):
    """ Simply removes the format extension no matter how long it is. """

    get_extension = len(str(files_path).split(".")[-1])
    clean_path = str(files_path)[:-get_extension]

    return clean_path


def generate_random(value_min, value_max):
    """ Generates random number. """

    generated_value = random.randint(value_min, value_max)

    return generated_value


def write_to_json(json_path, data):
    """ Create and write to json file """

    with open(json_path, 'w') as f:
        json.dump(data, f, indent=6)


def read_json(json_path):
    """ Reads json file """

    with open(json_path) as f:
        json_file = json.loads(f.read())

    return (json_file)


def check_path_exists(path):
    """ Check if path exists, if not, create it. """

    if os.path.exists(path) != True:
        os.mkdir(path)

    return True


def return_current_time_H_M():
    """ Return time in format 14:30 """
    time_struct = time.localtime(time.time())
    formatted_time = time.strftime("%H:%M", time_struct)
    return formatted_time


def convert_to_timestamp(time_str):
    """ convert a str 14:30 format to a timestamp. """
    current_date = time.localtime()[:3]
    time_str_with_date = f"{current_date[0]}-{current_date[1]}-{current_date[2]} {time_str}"
    time_struct = time.strptime(time_str_with_date, "%Y-%m-%d %H:%M")
    return time.mktime(time_struct)


def get_dates_new():
    """ Returns a lot of date stuff! """

    return {'date_now':  (str(datetime.datetime.now()).split(' ')[0]),  # 2024-06-22
            # 00:23:02.199620
            'date_time': (str(datetime.datetime.now()).split(' ')[1]),
            'day_num': datetime.datetime.today().day,
            'day_name': calendar.day_name[datetime.date.today().weekday()],
            'date_year':  datetime.datetime.today().year,
            'day_month_num':  datetime.datetime.today().month,
            'day_month_name': calendar.month_name[datetime.datetime.today().month],
            'date_now_full': datetime.datetime.now(),
            'current_time': datetime.datetime.now().time()
            }


def is_internet_available():
    try:
        response = requests.get("http://www.google.com", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        print("No Internet.")
        pass
    return False


def start_time():
    """ Prints when an API is called. """
    start_time = time.time()
    return start_time


def calculate_request_time(start_time, to_print=False):
    """ Calculates the Database queries. """
    end_time = time.time()
    elapsed_time = end_time - start_time
    if to_print:
        print(Fore.YELLOW, 'DB time: ', elapsed_time, Style.RESET_ALL)
    return elapsed_time


def generate_random_code(length=5):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


if __name__ == "__main__":
    print(is_internet_available())
