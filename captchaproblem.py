#!/usr/bin/env python
import base64
import contextlib
import json
import os
import selenium.webdriver as webdriver
import sys
import time
from google_alerts import GoogleAlerts
from argparse import ArgumentParser
import pickle
PY2 = False
if sys.version_info[0] < 3:
    PY2 = True

AUTH_COOKIE_NAME = 'SIDCC'
CONFIG_PATH = os.path.expanduser('~/.config/google_alerts')
CONFIG_FILE = os.path.join(CONFIG_PATH, 'config.json')
SESSION_FILE = os.path.join(CONFIG_PATH, 'session')
CONFIG_DEFAULTS = {'email': '', 'password': '', 'py2': PY2}

def obfuscate(p, action):
    key = "ru7sll3uQrGtDPcIW3okutpFLo6YYtd5bWSpbZJIopYQ0Du0a1WlhvJOaZEH"
    s = list()
    if action == 'store':
        if PY2:
            for i in range(len(p)):
                kc = key[i % len(key)]
                ec = chr((ord(p[i]) + ord(kc)) % 256)
                s.append(ec)
            return base64.urlsafe_b64encode("".join(s))
        else:
            return base64.urlsafe_b64encode(p.encode()).decode()
    else:
        if PY2:
            e = base64.urlsafe_b64decode(p)
            for i in range(len(e)):
                kc = key[i % len(key)]
                dc = chr((256 + ord(e[i]) - ord(kc)) % 256)
                s.append(dc)
            return "".join(s)
        else:
            e = base64.urlsafe_b64decode(p)
            return e.decode()


def main():
    parser = ArgumentParser()
    setup_parser = parser.add_subparsers(dest='cmd')
    seed_parser = setup_parser.add_parser('seed')
    seed_parser.add_argument('-d', '--driver', dest='driver',
                              required=True, type=str,
                              help='Location of the Chrome driver. This can be downloaded by visiting http://chromedriver.chromium.org/downloads',)
    seed_parser.add_argument('-t', '--timeout', dest='timeout',
                              required=False, type=int, default=20)
    args = parser.parse_args()

    config = json.load(open(CONFIG_FILE))
    if config.get('py2', PY2) != PY2:
        raise Exception("Python versions have changed. Please run `setup` again to reconfigure the client.")
    if config['password'] == '':
        raise Exception("Run setup before any other actions!")

    if args.cmd == 'seed':
        config['password'] = obfuscate(str(config['password']), 'fetch')
        ga = GoogleAlerts(config['email'], config['password'])
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        with contextlib.closing(webdriver.Chrome(args.driver, options=chrome_options)) as driver:
            # driver.get(ga.LOGIN_URL)
            # wait = ui.WebDriverWait(driver, 10) # timeout after 10 seconds
            # inputElement = driver.find_element_by_class_name('Email')
            # inputElement.send_keys(config['email'])
            # inputElement.submit()
            # print("[*] Filled in email address and submitted.")
            # time.sleep(30)
            # inputElement = driver.find_element_by_id('Passwd')
            # inputElement.send_keys(config['password'])
            # inputElement.submit()

            driver.get('https://stackoverflow.com/users/signup?ssrc=head&returnurl=%2fusers%2fstory%2fcurrent%27')
            time.sleep(3)
            driver.find_element_by_xpath('//*[@id="openid-buttons"]/button[1]').click()
            driver.find_element_by_xpath('//input[@type="email"]').send_keys(config['email'])
            driver.find_element_by_xpath('//*[@id="identifierNext"]').click()
            time.sleep(10)
            time.sleep(3)
            driver.find_element_by_xpath('//input[@type="password"]').send_keys(config['password'])
            driver.find_element_by_xpath('//*[@id="passwordNext"]').click()
            time.sleep(3)
            driver.get('https://www.google.com/alerts')
            print("[*] Filled in password and submitted.")
            print("[!] Waiting for the authentication cookie or %d seconds" % args.timeout)
            for _ in range(0, args.timeout):
                cookies = driver.get_cookies()
                if [x for x in cookies if x['name'] == AUTH_COOKIE_NAME]:
                    break
                time.sleep(1)
            collected = dict()
            for cookie in cookies:
                collected[str(cookie['name'])] = str(cookie['value'])
            with open(SESSION_FILE, 'wb') as f:
                pickle.dump(collected, f, protocol=2)
        print("[$] Session has been seeded, google-alerts is ready for use.")


if __name__ == '__main__':
    main()
