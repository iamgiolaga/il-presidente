import requests
import schedule
from datetime import datetime, timedelta
from utils.constants import token, hosting_url, port
from telegram.ext import Updater

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


def job(updater_instance):
    match_day_id = get_match_day_id()
    next_day = get_next_day(match_day_id)
    date_time = datetime.strptime(next_day, date_time_format)
    current_time = datetime.utcnow()
    time_difference = date_time - current_time
    if time_difference == timedelta(hours=2):
        dispatcher = updater_instance.dispatcher
        dispatcher.bot.sendMessage("Ricordatevi la formazione!")


if __name__ == '__main__':
    updater = Updater(token=token, use_context=True)
    updater.start_webhook(listen="0.0.0.0", webhook_url=f'{hosting_url}/{token}', url_path=token, port=int(port))

    schedule.every().minute().do(job(updater))
    # schedule.every().hour.at(":00").do(job(updater))
    # schedule.every().hour.at(":15").do(job(updater))
    # schedule.every().hour.at(":30").do(job(updater))
    # schedule.every().hour.at(":45").do(job(updater))
