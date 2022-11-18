import requests
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import configparser
import schedule
import time
from datetime import date, datetime
import os
from retry import retry

config = configparser.ConfigParser()
config.read('cfg.ini')
telefono = config['main']['telefono']
software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
user_agent = user_agent_rotator.get_random_user_agent()

@retry(ConnectionError, tries=10, delay=10)
def check():
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.algerietelecom.dz',
        'Referer': 'https://www.algerietelecom.dz/en/particuliers/idoom-adsl-prod3',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': f'{user_agent}',
        'X-Requested-With': 'XMLHttpRequest',
    }
    data = {
        'telephone': fr'{telefono}',
    }
    try:
        response = requests.post('https://www.algerietelecom.dz/en/numeligible', headers=headers, data=data)
    except requests.exceptions.ConnectionError:
        print(f'[!] Connection error retrying shortly ')
    except requests.exceptions.HTTPError:
        print(f'[!] Rate limited or the website is down for maintenance, the program will halt now')
        input()

    if 'desole' not in response.json()['type']:
        print(
            f'[!!!][ {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] MANUALLY CHECK VDSL ON AT WEBSITE, SOMETHING CHANGED.')
        # ADD FUNC TO BEEP A SOUND ? (requires a lot of dependencies for crossplatform compatibility, ie: msf c++ build toos)
        # You can also blink an LED  with GPIO if you're using a single board computer.
        e = input('Press any button to exit')
        if e: exit(0)
    else:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(
            f'[*][ {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Nothing changed so far, big sad checking again in 24 hours.')


if __name__ == '__main__':
    while True:
        schedule.every(24).hours.do(check)
        print(f'[!] Scheduled to check for VDSL compatibility every 24 hours.')
        while True:
            schedule.run_pending()
            time.sleep(1)
