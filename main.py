import os
import sys
import requests
import schedule
from time import sleep

import lib.utils as utils
import lib.save_data as save_data
import lib.notification as notification

root_dir = os.path.dirname(__file__)
sys.path.append(root_dir)

BotNot = notification.Notification()

global settings


def run():
    """  Run. """

    global settings
    has_started = False
    schedule.every(settings.get('interval_min')).minutes.do(ping_apps)

    while True:

        settings = utils.read_json(os.path.join(root_dir, "configs", "main.json"))  # nopep8

        start_time = utils.start_time()
        schedule.run_pending()
        res_time = utils.calculate_request_time(start_time)

        data = {
            "res_time": res_time,
            "last_pinged": str(utils.get_dates_new()['date_now_full'])
        }

        if has_started:
            save_data.save_data(None, "mr_ping_ping", data)

        has_started = True
        sleep(5)


def ping_ping(to_ping):
    """ Does a ping and returns response + data. """

    start_time = utils.start_time()

    if to_ping:
        try:
            response = requests.get(to_ping, timeout=5)
        except requests.RequestException:
            response = False

    res_time = utils.calculate_request_time(start_time)
    return response, res_time


def ping_apps():
    """ Pings apps and their given endpoints. """

    apps = utils.read_json(os.path.join(root_dir, 'configs/ping-apps.json'))

    if utils.is_internet_available():
        for app in apps:

            slug = app.get('slug')
            notify = app.get('notify')
            to_ping = app.get('active')
            base_url = app.get('base_url')
            endpoints = app.get('endpoints')

            is_endpoints = len(endpoints) > 0

            if to_ping:
                if is_endpoints:

                    endpoints_res = []
                    for endpoint in endpoints:

                        url_to_ping = f"{base_url}{endpoint}"
                        res, res_time = ping_ping(url_to_ping)
                        code = res.status_code if res else 500
                        success = code == 200

                        print_Status(slug, success, code, res_time)
                        report(app, code) if notify and not success else None

                        data = {
                            "endpoint": endpoint,
                            "full_url": url_to_ping,
                            "res_time": res_time,
                            "response": {
                                "code": code,
                                "success": success,
                                "data": res.json() if success else None
                            }
                        }

                        endpoints_res.append(data)

                    date_time = utils.get_dates_new()['date_now_full']
                    data = {
                        "date_time": str(date_time),
                        "pinged": app.get('slug'),
                        "success": success,
                        "endpoints_res": endpoints_res
                    }
                    save_data.save_data(slug, "pings", data)
                    sleep(1)

                else:
                    url_to_ping = f"{base_url}"
                    res, res_time = ping_ping(url_to_ping)
                    code = res.status_code if res else 500
                    success = code == 200

                    print_Status(slug, success, code, res_time)
                    report(app, code) if notify and not success else None

                    data = {
                        "endpoint": None,
                        "full_url": url_to_ping,
                        "res_time": res_time,
                        "response": {
                            "code": code,
                            "success": success,
                            "data": None
                        }
                    }

                    date_time = utils.get_dates_new()['date_now_full']
                    data = {
                        "date_time": str(date_time),
                        "pinged": app.get('slug'),
                        "success": success,
                        "endpoints_res": data
                    }
                    save_data.save_data(slug, "pings", data)
                    sleep(1)


def report(app, code):
    """ Sends a telegram message to admin. """

    if settings.get('notifications'):
        txt_1 = "👨‍🚀 Mr-Ping-Ping:\n\n"
        txt_2 = f"❌No Response: {app.get('slug')} : {code}"
        BotNot.send_ADMIN_notification(txt_1 + txt_2)


def print_Status(name, success, code, res_time):
    """ Prints response """
    print(
        f"Mr-Ping-Ping: Checked - {name} | Res: {success} - {code} | Time: {res_time}")


if __name__ == '__main__':
    print('Starting')
    settings = utils.read_json(os.path.join(root_dir, "configs", "main.json"))  # nopep8

    while True:
        try:
            run()
        except Exception as e:
            print(e)
            sleep(25)
