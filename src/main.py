#!/usr/bin/python
# -*- coding: utf-8 -*-
# Waluty 1.1.0 - currency converter for the Nokia N9 (Python 2.6 + PySide + QML)
# Written by Claude (Anthropic) together with smyhu.

import os
import sys
import signal
import subprocess

import json

from PySide.QtCore import QObject, QUrl, QProcess, Signal, Slot
from PySide.QtGui import QApplication
from PySide.QtDeclarative import QDeclarativeView

import common
from common import APP_DIR


class Feed(QObject):
    """Posts the rates of favourite currencies to the Events (Feed) screen."""

    @Slot()
    def clear(self):
        common.feed_clear()

    @Slot(unicode, unicode)
    def publish(self, title, body):
        common.feed_publish(title, body)


class Service(QObject):
    """Starts the background refresh service (tlo.py) if it is not running,
    and tells it to re-read the settings."""

    @Slot()
    def wake(self):
        pid = common.service_pid()
        if pid:
            try:
                os.kill(pid, signal.SIGUSR1)
            except OSError:
                pass
            return
        try:
            devnull = open(os.devnull, 'r+')
            subprocess.Popen([sys.executable, os.path.join(APP_DIR, 'tlo.py')],
                             stdin=devnull, stdout=devnull, stderr=devnull,
                             close_fds=True, preexec_fn=os.setsid)
        except OSError, e:
            print 'waluty: cannot start background service:', e


class Downloader(QObject):
    """Downloads URLs in helper processes, so a crash can only end a helper.
    HTTPS goes through waluty-fetch, a small native Qt program: QtNetwork
    inside Python crashes on the N9, because Python already holds the old
    OpenSSL 0.9.8 while the TLS patch makes Qt load OpenSSL 1.0.x.
    Plain HTTP goes through Python's urllib2 (fetch.py)."""

    done = Signal()

    def __init__(self):
        QObject.__init__(self)
        self.results = []
        self.procs = []

    @Slot(unicode, unicode)
    def get(self, tag, urls):
        attempts = []
        urls = urls.split()
        for u in urls:
            if u.startswith('https:'):
                attempts.append(('native', u))
            else:
                attempts.append(('py', u))
                attempts.append(('native', u))
        self._next(tag, attempts)

    def _next(self, tag, attempts):
        if not attempts:
            self.results.append({'tag': tag, 'ok': False, 'text': ''})
            self.done.emit()
            return
        mode, url = attempts[0]
        print 'waluty: GET %s (%s)' % (url, mode)
        proc = QProcess(self)
        self.procs.append(proc)

        def finished(*args):
            code, status = proc.exitCode(), proc.exitStatus()
            out = str(proc.readAllStandardOutput())
            err = str(proc.readAllStandardError()).strip()
            self.procs.remove(proc)
            proc.deleteLater()
            ok = status == QProcess.NormalExit and code == 0 and len(out) > 0
            if ok:
                print 'waluty:   ok, %d bytes' % len(out)
                self.results.append({'tag': tag, 'ok': True, 'text': out.decode('utf-8', 'replace')})
                self.done.emit()
            else:
                how = 'crashed' if status != QProcess.NormalExit else 'exit %d' % code
                print 'waluty:   failed (%s) %s' % (how, err)
                self._next(tag, attempts[1:])

        proc.finished.connect(finished)
        if mode == 'native':
            proc.start(os.path.join(APP_DIR, 'waluty-fetch'), [url])
        else:
            proc.start(sys.executable, [os.path.join(APP_DIR, 'fetch.py'), 'py', url])

    @Slot(result=unicode)
    def take(self):
        if not self.results:
            return u''
        return unicode(json.dumps(self.results.pop(0)))


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('waluty')
    app.setOrganizationName('waluty')

    lang = common.phone_language()

    view = QDeclarativeView()
    feed = Feed()
    downloader = Downloader()
    service = Service()
    service.wake()
    ctx = view.rootContext()
    ctx.setContextProperty('uiLang', lang)
    ctx.setContextProperty('feed', feed)
    ctx.setContextProperty('downloader', downloader)
    ctx.setContextProperty('service', service)
    # WALUTY_NONET=1 starts without downloading rates (for troubleshooting)
    ctx.setContextProperty('noNet', os.environ.get('WALUTY_NONET') == '1')
    view.setResizeMode(QDeclarativeView.SizeRootObjectToView)
    view.setSource(QUrl.fromLocalFile(os.path.join(APP_DIR, 'qml', 'main.qml')))
    view.showFullScreen()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
