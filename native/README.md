# waluty-fetch

A tiny native Qt 4.7 program that downloads one URL to stdout. Waluty uses it for HTTPS.

On the N9, Python 2.6 carries OpenSSL 0.9.8, while the community TLS 1.2 patch makes QtNetwork
load OpenSSL 1.0.x. With both in one Python process, any HTTPS request through Qt crashes.
A separate native process avoids the clash.

`waluty-fetch-armel` is the prebuilt binary (ARMv7, hard-float, glibc 2.10, links only
libQtNetwork, libQtCore and libc). It was cross-compiled with clang against the Nokia
Harmattan PR1.3 libraries, without moc, as plain `main()` code.
