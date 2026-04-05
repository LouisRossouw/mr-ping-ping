import os
import logging
import requests
from datetime import datetime
from logging.handlers import RotatingFileHandler

from core.utils import write_to_json, is_internet_available, start_time, calculate_request_time
import core.save_data as save_data

this_dir = os.path.dirname(__file__)

handler = RotatingFileHandler(
    "data/service.log", maxBytes=1_000_000, backupCount=3)

console = logging.StreamHandler()

logging.basicConfig(
    handlers=[handler],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def run_action(settings, action_slug):
    st = start_time()

    if not is_internet_available():
        logging.info("No internet connection..")
        return

    action = settings.actions_by_slug[action_slug]

    if not action['active']:
        logging.info("%s - Ping not active", action_slug)
        return

    # TODO; Inlcude the method.
    # method = action.get("method", "GET")
    # payload = action.get("payload")

    success = False

    slug = action.get('slug')
    notify = action.get('notify')
    to_ping = action.get('active')
    base_url = action.get('base_url')
    endpoints = action.get('endpoints')

    is_endpoints = len(endpoints) > 0
    if to_ping:

        date_now = datetime.now()

        if is_endpoints:

            endpoints_res = []
            for endpoint in endpoints:

                url_to_ping = f"{base_url}{endpoint}"
                res, res_time = ping_ping(url_to_ping)
                code = res.status_code if res else 500
                success = code == 200

                print_Status(slug, success, code, res_time)
                report(url_to_ping, action, code,
                       settings) if notify and not success else None

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

            data = {
                "date_time": str(date_now),
                "timestamp": date_now.timestamp(),
                "datetime": date_now.strftime("%d-%m-%Y %H:%M"),
                "pinged": slug,
                "success": success,
                "endpoints_res": endpoints_res
            }
            save_data.save_data(slug, "pings", data)

        else:
            url_to_ping = f"{base_url}"
            res, res_time = ping_ping(url_to_ping)
            code = res.status_code if res else 500
            success = code == 200

            print_Status(slug, success, code, res_time)
            report(url_to_ping, action, code,
                   settings) if notify and not success else None

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

            data = {
                "date_time": str(date_now),
                "timestamp": date_now.timestamp(),
                "datetime": date_now.strftime("%d-%m-%Y %H:%M"),
                "pinged": slug,
                "success": success,
                "endpoints_res": data
            }
            save_data.save_data(slug, "pings", data)

    elapsed_time = calculate_request_time(st)

    date_now = datetime.now()
    # manifest_path = os.path.join(
    #     settings.data_dir, f"{action_slug.replace('-', '_')}_manifest.json")

    # Ping Ping

    # System
    write_to_json(settings.service_path, data)

    data = {
        "success": success,
        "system_name": settings.name,
        "system_slug": settings.slug,
        "elapsed_time": elapsed_time,
        "timestamp": date_now.timestamp(),
        "datetime": date_now.strftime("%d-%m-%Y %H:%M"),
        "pinged": slug
    }

    # Manifest historic data
    save_data.save_data(None, "ping_ping", data)

    # TODO; Not using this, possibly remove.
    # Manifest last run
    # write_to_json(manifest_path, {
    #     "success": success,
    #     ** action,
    #     **data,
    # })


def print_Status(name, success, code, res_time):
    """ Prints response """
    print(
        f"Mr-Ping-Ping: Checked - {name} | Res: {success} - {code} | Time: {res_time}")


def report(url_to_ping, action, code, settings):
    """ Sends a telegram message to admin. """

    if settings.notifications:
        url = f"{settings.tele_jam_api_baseurl}/notify/bots/{settings.notify_bot}"
        requests.post(url=url, json=[f"🧩 {settings.name}:\n\n", (
            f"❌ Failed: {action['slug']}\n"
            f"❔ Is service online?🤔 code: {str(code)}\n"
            f"🔗 url {url_to_ping}\n"
        )])


def ping_ping(to_ping):
    """ Does a ping and returns response + data. """

    st = start_time()

    if to_ping:
        try:
            response = requests.get(to_ping, timeout=15)
        except requests.RequestException:
            response = False

    res_time = calculate_request_time(st)
    return response, res_time


if __name__ == "__main__":
    pass
