import functions_framework
import requests
import pytz
from datetime import datetime, timedelta
from constants import token, chat_id

date_time_format = '%Y-%m-%dT%H:%M:%SZ'
time_format = '%H:%M'
italian_tz = pytz.timezone('Europe/Rome')

def get_match_day_id():
    url = "https://www.legaseriea.it/api/season/157617/championship/A/matchday?lang=it"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()['data']
            for item in data:
                if item["category_status"] == "TO BE PLAYED":
                    return item["id_category"]
            return
        else:
            print(f'Errore: La richiesta ha restituito il codice di stato {response.status_code}')

    except requests.exceptions.RequestException as e:
        print(f'Errore: Impossibile eseguire la richiesta GET: {e}')


def get_next_day(match_day_id):
    url = f'https://www.legaseriea.it/api/stats/live/match?extra_link&order=oldest&lang=it&season_id=157617&page=1&limit=20&pag&match_day_id={match_day_id}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            matches = response.json()['data']['matches']
            return matches[0]['date_time']
        else:
            print(f'Errore: La richiesta ha restituito il codice di stato {response.status_code}')

    except requests.exceptions.RequestException as e:
        print(f'Errore: Impossibile eseguire la richiesta GET: {e}')


def compute_minutes_left(date_time):
    current_time = datetime.utcnow()
    time_diff = date_time - current_time
    days = time_diff.days
    seconds = time_diff.seconds
    minutes = seconds / 60
    return days*24*60 + minutes

def broadcast_channel(message):
    url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}'
    requests.get(url)

@functions_framework.http
def remind_squad(request):
    match_day_id = get_match_day_id()
    next_day = get_next_day(match_day_id)
    date_time = datetime.strptime(next_day, date_time_format)
    match_time = date_time.strftime(time_format)
    minutes_left = round(compute_minutes_left(date_time))

    match_time = date_time.replace(tzinfo=pytz.utc).astimezone(italian_tz)
    match_time_str = match_time.strftime(time_format)

    minutes_left = round(compute_minutes_left(date_time))

    if 90 <= minutes_left <= 120:
        broadcast_channel(f'Ricordatevi la formazione! Si gioca alle {match_time_str}!')
