# -*- coding: utf-8 -*-
# Waluty: code shared by the app (main.py) and the background service (tlo.py).
# Python 2.6 (Nokia N9). The download sources mirror qml/net.js.

import os
import glob
import pwd
import math
import time
import json
import subprocess
import datetime

APP_DIR = os.path.dirname(os.path.abspath(__file__))
FETCH = os.path.join(APP_DIR, 'waluty-fetch')
SOURCE_NAME = 'waluty'
ICON = '/usr/share/icons/hicolor/80x80/apps/waluty80.png'
LANGUAGES = ('pl', 'en', 'de', 'es', 'it', 'fr')
# home of the phone user. Not $HOME (aegis-exec keeps root's), and the password
# database gives /nonexistent under aegis-exec, so fall back to /home/user.
HOME = pwd.getpwuid(os.getuid()).pw_dir
if not os.path.isdir(HOME):
    HOME = '/home/user'
DATA_DIR = os.path.join(HOME, '.local/share/data/waluty')
DB_DIR = os.path.join(DATA_DIR, 'waluty/QML/OfflineStorage/Databases')
# per user, so a copy started by another account (e.g. over SSH) can't block it
PIDFILE = os.path.join(DATA_DIR, 'tlo.pid')
LOGFILE = os.path.join(DATA_DIR, 'tlo.log')

FEED_TITLES = {'pl': u'Kursy walut', 'en': u'Exchange rates', 'de': u'Wechselkurse',
               'es': u'Tipos de cambio', 'it': u'Tassi di cambio', 'fr': u'Taux de change'}

FIAT_URLS = ['https://open.er-api.com/v6/latest/USD', 'http://open.er-api.com/v6/latest/USD']
COINGECKO = {'BTC': 'bitcoin', 'ETH': 'ethereum', 'USDT': 'tether', 'BNB': 'binancecoin',
             'SOL': 'solana', 'XRP': 'ripple', 'USDC': 'usd-coin', 'ADA': 'cardano',
             'DOGE': 'dogecoin', 'LTC': 'litecoin'}
BINANCE = {'BTC': 'BTCUSDT', 'ETH': 'ETHUSDT', 'BNB': 'BNBUSDT', 'SOL': 'SOLUSDT',
           'XRP': 'XRPUSDT', 'ADA': 'ADAUSDT', 'DOGE': 'DOGEUSDT', 'LTC': 'LTCUSDT',
           'USDC': 'USDCUSDT'}


def log(msg):
    print 'waluty: %s' % msg
    # the background service has no console: keep a short log next to the data
    try:
        if os.path.exists(LOGFILE) and os.path.getsize(LOGFILE) > 20000:
            os.rename(LOGFILE, LOGFILE + '.old')
        f = open(LOGFILE, 'a')
        f.write('%s %s\n' % (time.strftime('%Y-%m-%d %H:%M:%S'), msg))
        f.close()
    except (IOError, OSError):
        pass


def session_env():
    """Outside the user session (upstart) D-Bus and gconf need the session bus
    address; Harmattan keeps it in /tmp/session_bus_address.user."""
    if os.environ.get('DBUS_SESSION_BUS_ADDRESS'):
        return
    try:
        for line in open('/tmp/session_bus_address.user'):
            if 'DBUS_SESSION_BUS_ADDRESS=' in line:
                value = line.split('DBUS_SESSION_BUS_ADDRESS=', 1)[1].strip().strip("';")
                os.environ['DBUS_SESSION_BUS_ADDRESS'] = value
    except IOError:
        pass


def phone_language():
    """Phone language (MeeGo gconf /meegotouch/i18n/language); English otherwise.
    WALUTY_LANG=de etc. overrides it for testing."""
    code = os.environ.get('WALUTY_LANG', '')
    if not code:
        session_env()
        try:
            p = subprocess.Popen(['gconftool-2', '-g', '/meegotouch/i18n/language'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            code = p.communicate()[0].strip()
        except OSError:
            pass
    if not code:
        code = os.environ.get('LANG', '')
    code = code[:2].lower()
    if code in LANGUAGES:
        return code
    return 'en'


# ---- Events feed (MEventFeed D-Bus service) ----

def _session_bus():
    import dbus
    session_env()
    return dbus.SessionBus()


def _feed_iface():
    import dbus
    obj = _session_bus().get_object('com.nokia.home.EventFeed', '/eventfeed')
    return dbus.Interface(obj, 'com.nokia.home.EventFeed')


def feed_clear():
    try:
        _feed_iface().removeItemsBySourceName(SOURCE_NAME)
    except Exception, e:
        log('feed clear failed: %s' % e)


def feed_publish(title, body):
    try:
        import dbus
        iface = _feed_iface()
        iface.removeItemsBySourceName(SOURCE_NAME)
        iface.addItem(dbus.Dictionary({
            'icon': ICON,
            'title': title,
            'body': body,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            'sourceName': SOURCE_NAME,
            'sourceDisplayName': 'Waluty',
        }, signature='sv'))
    except Exception, e:
        log('feed publish failed: %s' % e)


# ---- number format, same as format() in qml/data.js ----

def format_value(value, lang):
    a = abs(value)
    if a == 0:
        s = '0'
    elif a >= 1:
        s = '%.2f' % value
    else:
        # 4 significant digits, e.g. 0.00001257 BTC
        decimals = min(12, 3 - int(math.floor(math.log10(a))))
        s = '%.*f' % (decimals, value)
    neg = s.startswith('-')
    if neg:
        s = s[1:]
    parts = s.split('.')
    dec = '.' if lang == 'en' else ','
    sep = ',' if lang == 'en' else (' ' if lang in ('pl', 'fr') else '.')
    ip = parts[0]
    groups = []
    while len(ip) > 3:
        groups.insert(0, ip[-3:])
        ip = ip[:-3]
    groups.insert(0, ip)
    out = sep.join(groups)
    if len(parts) > 1:
        out += dec + parts[1]
    return ('-' if neg else '') + out


def feed_body(rates, favourites, base, lang):
    lines = []
    for code in favourites:
        if len(lines) >= 4:
            break
        if code == base or not rates.get(code) or not rates.get(base):
            continue
        lines.append(u'1 %s = %s %s' % (code, format_value(rates[base] / rates[code], lang), base))
    return u'   ·   '.join(lines)


# ---- settings database shared with the QML app (qml/storage.js) ----

def db_file():
    """The SQLite file QML's openDatabaseSync("waluty") created, or None."""
    for ini in glob.glob(os.path.join(DB_DIR, '*.ini')):
        try:
            text = open(ini).read()
        except IOError:
            continue
        if 'Name=waluty' in text:
            path = ini[:-4] + '.sqlite'
            if os.path.exists(path):
                return path
    return None


class Settings(object):
    def __init__(self, path):
        import sqlite3
        self.conn = sqlite3.connect(path, timeout=10)

    def get(self, key, fallback):
        row = self.conn.execute('SELECT value FROM settings WHERE key = ?', (key,)).fetchone()
        return row[0] if row else fallback

    def set(self, key, value):
        self.conn.execute('INSERT OR REPLACE INTO settings VALUES(?, ?)', (key, unicode(value)))
        self.conn.commit()

    def close(self):
        self.conn.close()


# ---- downloads ----

def has_network():
    """True when there is a default route (Wi-Fi or mobile data is up).
    Checked first so the service never makes the phone ask for a connection."""
    try:
        for line in open('/proc/net/route').readlines()[1:]:
            fields = line.split()
            if len(fields) > 2 and fields[1] == '00000000':
                return True
    except IOError:
        pass
    return False


def fetch(url):
    """Body of url or None. HTTPS through the native helper (see main.py)."""
    try:
        if url.startswith('https:'):
            p = subprocess.Popen([FETCH, url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            if p.returncode == 0 and out:
                return out
            log('GET %s failed (%s) %s' % (url, p.returncode, err.strip()))
            return None
        import urllib2
        return urllib2.urlopen(url, timeout=25).read()
    except Exception, e:
        log('GET %s failed: %s' % (url, e))
        return None


def fetch_json(urls):
    for url in urls:
        body = fetch(url)
        if body:
            try:
                return json.loads(body)
            except ValueError:
                log('bad JSON from %s' % url)
    return None


def fetch_crypto():
    q = '/api/v3/simple/price?vs_currencies=usd&ids=' + ','.join(COINGECKO.values())
    obj = fetch_json(['https://api.coingecko.com' + q])
    if obj:
        rates = {}
        for code, cg in COINGECKO.items():
            usd = obj.get(cg, {}).get('usd', 0)
            if usd > 0:
                rates[code] = 1.0 / usd
        return rates
    # Binance prices are in USDT; USDT from the USDC/USDT pair, USDC = 1 USD
    path = '/api/v3/ticker/price?symbols=%5B' + ','.join(['%22' + s + '%22' for s in BINANCE.values()]) + '%5D'
    lst = fetch_json(['https://data-api.binance.vision' + path, 'http://data-api.binance.vision' + path])
    if not lst:
        return None
    price = dict((item['symbol'], float(item['price'])) for item in lst)
    usdt = price.get('USDCUSDT') or 1.0
    rates = {'USDT': usdt, 'USDC': 1.0}
    for code, pair in BINANCE.items():
        if code != 'USDC' and price.get(pair, 0) > 0:
            rates[code] = usdt / price[pair]
    return rates


def fetch_rates(old):
    """Merged rates (units per 1 USD) or None when fiat rates failed.
    Missing crypto rates keep their previous values, as the app does."""
    obj = fetch_json(FIAT_URLS)
    if not obj or obj.get('result') != 'success':
        return None
    rates = dict(obj['rates'])
    crypto = fetch_crypto()
    if crypto:
        rates.update(crypto)
    else:
        for code in COINGECKO:
            if code in old and code not in rates:
                rates[code] = old[code]
    return rates


# ---- background service process ----

def service_pid():
    """Pid of the running service or None. The pid file survives a reboot,
    so the process must really be tlo.py, not a newer one with the same pid."""
    try:
        pid = int(open(PIDFILE).read().strip())
        if 'tlo.py' not in open('/proc/%d/cmdline' % pid).read():
            return None
        return pid
    except (IOError, ValueError, OSError):
        return None
