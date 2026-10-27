#!/usr/bin/python
# -*- coding: utf-8 -*-
# Waluty background service: refreshes rates and the Events feed entry every
# few hours (Settings > Background refresh), also when the app is closed.
# Started at login by /etc/init/apps/waluty-tlo.conf (as root, then it
# switches to the phone user) and, as a fallback, by the app itself.
# SIGUSR1 makes it re-read the settings at once.

import os
import sys
import json
import time
import signal


def become_user(name='user'):
    """Started by upstart as root: continue as the phone user. On the N9
    aegis-exec -u user gives 'nobody' and Aegis forbids even root to call
    setgroups()/setuid(), so the script restarts itself through devel-su.
    Must run before common is imported, as common derives paths from the uid."""
    if os.getuid() != 0:
        return
    os.execvp('devel-su', ['devel-su', name, '-c', os.path.abspath(__file__)])


become_user()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import log

CHECK = 15 * 60          # longest sleep, also the retry delay after a failure


def woken(signum, frame):
    pass                 # only interrupts time.sleep()


def cycle():
    """One check. Returns seconds to sleep."""
    path = common.db_file()
    if not path:
        return CHECK     # the app has never been started
    s = common.Settings(path)
    try:
        hours = int(s.get('interval', '3'))
        if hours <= 0:
            return CHECK
        last = int(float(s.get('ratesTime', '0'))) / 1000.0
        due = last + hours * 3600 - time.time()
        if due > 60:
            return min(due, CHECK)
        if not common.has_network():
            return CHECK
        try:
            old = json.loads(s.get('rates', '{}'))
        except ValueError:
            old = {}
        log('background refresh')
        rates = common.fetch_rates(old)
        if not rates:
            return CHECK
        s.set('rates', json.dumps(rates))
        s.set('ratesTime', int(time.time() * 1000))
        if s.get('feed', '1') == '1':
            lang = common.phone_language()
            favourites = s.get('favourites', 'USD,EUR,GBP,PLN,BTC').split(',')
            body = common.feed_body(rates, favourites, s.get('base', 'USD'), lang)
            if body:
                common.feed_publish(common.FEED_TITLES[lang], body)
        log('background refresh done')
        return min(hours * 3600, CHECK)
    finally:
        s.close()


def main():
    if common.service_pid():
        return 0         # already running
    if not os.path.isdir(common.DATA_DIR):
        os.makedirs(common.DATA_DIR)
    open(common.PIDFILE, 'w').write(str(os.getpid()))
    log('background service started (pid %d, user %s)' % (os.getpid(), common.HOME))
    signal.signal(signal.SIGUSR1, woken)
    while True:
        try:
            delay = cycle()
        except Exception, e:
            log('background error: %s' % e)
            delay = CHECK
        time.sleep(max(delay, 30))


if __name__ == '__main__':
    sys.exit(main())
