// Waluty download helper for the Nokia N9.
// Usage: waluty-fetch URL  -> response body on stdout, exit code 0 on success.
// Native Qt program: Python on the N9 carries the old OpenSSL 0.9.8, which
// crashes the TLS-patched QtNetwork (OpenSSL 1.0.x) in the same process.
// Built without moc: only existing signals and slots are connected.

#include <QtCore/qcoreapplication.h>
#include <QtCore/qeventloop.h>
#include <QtCore/qtimer.h>
#include <QtCore/qurl.h>
#include <QtNetwork/qnetworkaccessmanager.h>
#include <QtNetwork/qnetworkrequest.h>
#include <QtNetwork/qnetworkreply.h>
#include <stdio.h>

int main(int argc, char **argv)
{
    QCoreApplication app(argc, argv);
    if (argc < 2) {
        fprintf(stderr, "usage: waluty-fetch URL\n");
        return 1;
    }
    QNetworkAccessManager nam;
    QNetworkRequest request(QUrl::fromEncoded(argv[1]));
    request.setRawHeader("User-Agent", "Waluty/1.0 (Nokia N9)");
    QNetworkReply *reply = nam.get(request);

    QEventLoop loop;
    QObject::connect(reply, SIGNAL(finished()), &loop, SLOT(quit()));
    QTimer::singleShot(25000, &loop, SLOT(quit()));
    loop.exec();

    if (!reply->isFinished()) {
        fprintf(stderr, "timeout\n");
        return 3;
    }
    int status = reply->attribute(QNetworkRequest::HttpStatusCodeAttribute).toInt();
    if (reply->error() != QNetworkReply::NoError || status != 200) {
        fprintf(stderr, "error %d, HTTP %d: %s\n", int(reply->error()), status,
                reply->errorString().toLocal8Bit().constData());
        return 2;
    }
    QByteArray body = reply->readAll();
    fwrite(body.constData(), 1, body.size(), stdout);
    return 0;
}
