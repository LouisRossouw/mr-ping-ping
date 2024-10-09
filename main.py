import os
import lib.test as utils
import sys
import settings
import schedule
from time import sleep
import requests

SETTINGS = settings.Settings()
sys.path.append(SETTINGS.root_dir)


def pingping(to_ping):
    """ Does a ping and returns response + data. """
    base_url = to_ping.get('base_url')

    start_time = utils.start_time()

    if base_url:
        try:
            response = requests.get(base_url, timeout=5)
        except requests.RequestException:
            response = False

    res_time = utils.calculate_request_time(start_time)
    return response, res_time


def something():
    """ Runs """

    apps = utils.read_json(os.path.join(SETTINGS.root_dir, 'ping-apps.json'))

    if utils.is_internet_available():
        for app in apps:

            base_url = app.get('base_app')
            endpoints = app.get('apps')

            for endpoint in endpoints:

                url_to_ping = f"{base_url}{endpoint}"

                response, res_time = pingping(url_to_ping)
                success = response.status_code == 200

                print(f"Checked - {app.get('slug')} | Res: {success} - {response.status_code} | Time: {res_time}")  # nopep8

                sleep(1)

        data = {
            "timestamp": "",
            "time_formatted": "",
            "pinged": app.get('slug'),
            "endpoints_res": [
                {
                    "endpoint": "/health",
                    "full_url": "https://www.rockettothesky.com/health",
                    "response": {
                        "code": 200,
                        "success": True,
                        "data": []
                    }

                },
            ]

        }

        # app_utils.save_data(account, data)


def run():
    """  Run. """
    schedule.every(0.02).minutes.do(something)

    while True:
        schedule.run_pending()
        sleep(5)


if __name__ == '__main__':

    print('Starting')

    while True:
        try:
            run()
        except Exception as e:
            print(e)
            sleep(25)
