import os
from datetime import datetime
from core.utils import read_json, get_data, go_back_time, go_forward_in_time, maybe_append, filter_range
from core.database import DatabaseManager
from fastapi import HTTPException


def pause_schedule(scheduler, job_id):
    """ Pauses a specific job id in the scheduler. """

    if scheduler:
        if job_id:
            scheduler.scheduler.pause_job(job_id)
            return {"status": f"job {job_id} paused"}

        paused_jobs = []
        for job in scheduler.scheduler.get_jobs():
            paused_jobs.append(job.id)
            job.pause()

        return {"status": f"Paused {len(paused_jobs)} job(s)"}
    return {"error": "no scheduler attached"}


def resume_job(scheduler, job_id):
    """ Resumes a specific job id in the scheduler. """

    if scheduler:
        if job_id:
            scheduler.scheduler.resume_job(job_id)
            return {"status": f"job {job_id} resumed"}

        resumed_jobs = []
        for job in scheduler.scheduler.get_jobs():
            scheduler.scheduler.resume_job(job.id)
            resumed_jobs.append(job.id)

        return {"status": f"Resumed {len(resumed_jobs)} job(s)"}

    return {"error": "no scheduler attached"}


def shutdown_scheduler(scheduler):
    """ Stops the schduleer, can't be restarted onces stopped. """

    if scheduler:
        scheduler.scheduler.shutdown(wait=False)
        return {"status": "scheduler shutdown"}
    return {"error": "no scheduler attached"}


def restart_scheduler(scheduler):
    return {"status": "TODO; Restart service"}


def status_scheduler():
    return {"status": "TODO; Get Active jobs."}


def health(settings):
    """ Returns the health of the service. """

    data_exists = os.path.exists(settings.service_path)
    data = {} if not data_exists else read_json(settings.service_path)
    return {"ok": True, **data}


def get_ping_apps(settings, app):
    """ Returns a specific apps config. """

    actions = settings.actions

    if not app:
        return actions

    try:
        return next(a for a in actions if a.get("slug") == app)
    except StopIteration:
        raise HTTPException(status_code=404, detail="App not found")


def get_data_for_app(data_dir):
    data = get_data('hour', 1, data_dir)

    for d in data:
        _data = read_json(d)

    _, info = list(_data.items())[-1]

    return _, info


def get_ping_apps_status(settings, app):
    """ Return the status of all apps or specific within the config. """

    if settings.use_postgresql:
        db = DatabaseManager(settings)
        if app:
            ping = db.get_latest_ping(app)
            return ping.stats if ping else None

        apps_status = []
        for action in settings.actions:
            app_slug = action.get('slug')
            ping = db.get_latest_ping(app_slug)
            if ping:
                apps_status.append(ping.stats)
        return apps_status

    actions = settings.actions
    pings_data_dir = settings.pings_data_dir

    if app:
        data_dir = os.path.join(pings_data_dir, app)

        if not os.path.exists(data_dir):
            return None

        _, info = get_data_for_app(data_dir)

        return info

    apps_status = []
    for action in actions:
        app_slug = action.get('slug')
        data_dir = os.path.join(pings_data_dir, app_slug)

        if not os.path.exists(data_dir):
            continue

        _, info = get_data_for_app(data_dir)

        if (info):
            apps_status.append(info)

    return apps_status


def get_ping_apps_data(settings, app, range, interval):
    """ Returns the relevant data for a given range and interval """

    if settings.use_postgresql:
        db = DatabaseManager(settings)
        data_range = filter_range(range, interval)
        start_time = data_range['search_from']
        pings = db.get_pings(app, start_time)

        clean = []
        no_duplicates_list = []
        for ping in pings:
            date_str = str(ping.timestamp)
            value_data = maybe_append(date_str, range, interval)
            if value_data not in no_duplicates_list:
                no_duplicates_list.append(value_data)
                clean.append({
                    'date': date_str,
                    'endpoints_res': ping.stats.get('endpoints_res')
                })
        return clean

    pings_data_dir = settings.pings_data_dir
    data_dir = os.path.join(pings_data_dir, app)

    if not os.path.exists(data_dir):
        return None

    data = get_data(range, interval, data_dir)

    for d in data:
        _data = read_json(d)
        for key, value in _data.items():
            try:
                time = datetime.strptime(key, "%Y-%m-%d %H:%M:%S.%f")
            except Exception:
                time = datetime.strptime(key, "%Y-%m-%d")

        start_time = go_back_time(time, range, interval)
        test = go_forward_in_time(time, range, 2)

    clean = []
    no_duplicates_list = []

    for d in data:
        _data = read_json(d)

        for date, value in _data.items():
            try:
                time = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
            except Exception:
                time = datetime.strptime(date, "%Y-%m-%d")

            # TODO; Add two hours

            if start_time <= time:

                value_data = maybe_append(date, range,  interval)

                if value_data not in no_duplicates_list:
                    no_duplicates_list.append(value_data)

                    clean.append({
                        'date': date,
                        'endpoints_res': value.get('endpoints_res')
                    })

    return clean


def status_ping_ping(settings, interval, range):
    """ Returns the status of mr ping ping """

    if settings.use_postgresql:
        db = DatabaseManager(settings)
        ping = db.get_latest_ping('ping_ping')
        if not ping:
            return None
        return {
            'date': str(ping.timestamp),
            'res_time': ping.stats.get('res_time'),
            'last_pinged': ping.stats.get('last_pinged'),
        }

    mrpingping_data_dir = os.path.join(settings.data_dir, 'ping_ping')
    data = get_data(range, interval, mrpingping_data_dir)

    for d in data:
        _data = read_json(d)

    date, info = list(_data.items())[-1]

    return {
        'date': date,
        'res_time': info.get('res_time'),
        'last_pinged': info.get('last_pinged'),
    }
