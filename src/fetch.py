#!/usr/bin/python
# -*- coding: utf-8 -*-
# Waluty download helper. Runs as a separate process, so that a crash in the
# phone's SSL libraries can only end this helper, never the app itself.
# Usage: fetch.py qt|py URL   -> body on stdout, exit code 0 on success

import sys

TIMEOUT = 25


def fetch_py(url):
    import urllib2
    body = urllib2.urlopen(url, timeout=TIMEOUT).read()
    sys.stdout.write(body)
    return 0


def fetch_qt(url):
    from PySide.QtCore import QCoreApplication, QUrl, QTimer
    from PySide.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

    app = QCoreApplication(sys.argv)
    nam = QNetworkAccessManager()
    reply = nam.get(QNetworkRequest(QUrl(url)))
    result = [3]

    def finished():
        status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        if reply.error() == QNetworkReply.NoError and status == 200:
            sys.stdout.write(str(reply.readAll()))
            result[0] = 0
        else:
            sys.stderr.write('error %s, HTTP %s: %s\n' % (reply.error(), status, reply.errorString()))
            result[0] = 2
        app.quit()

    def ssl_errors(errors):
        for e in errors:
            sys.stderr.write('ssl: %s\n' % e.errorString())

    def timeout():
        sys.stderr.write('timeout\n')
        app.quit()

    reply.finished.connect(finished)
    reply.sslErrors.connect(ssl_errors)
    QTimer.singleShot(TIMEOUT * 1000, timeout)
    app.exec_()
    return result[0]


def main():
    mode, url = sys.argv[1], sys.argv[2]
    try:
        if mode == 'qt':
            return fetch_qt(url)
        return fetch_py(url)
    except Exception, e:
        sys.stderr.write('%s\n' % e)
        return 4


if __name__ == '__main__':
    sys.exit(main())
