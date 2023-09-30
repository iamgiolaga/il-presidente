import requests
import schedule
import time
from datetime import datetime, timedelta
from utils.constants import token, chat_id

date_time_format = '%Y-%m-%dT%H:%M:%SZ'

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


def compute_minutes_left(next_day):
    date_time = datetime.strptime(next_day, date_time_format)
    current_time = datetime.utcnow()
    time_diff = date_time - current_time
    days = time_diff.days
    seconds = time_diff.seconds
    minutes = seconds / 60
    return days*24*60 + minutes

def broadcast_channel(message):
    url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}'
    requests.get(url)

def job():
    match_day_id = get_match_day_id()
    next_day = get_next_day(match_day_id)
    minutes_left = compute_minutes_left(next_day)

    if round(minutes_left) == 110:
        broadcast_channel("Ricordatevi la formazione!")


if __name__ == '__main__':
    job()
