# Waluty: currency converter for the Nokia N9

*Opis po polsku poniżej.*

A currency converter for the Nokia N9 (MeeGo Harmattan PR1.3), written in 2026. It follows the
N9 UI guidelines, with a dark theme for the AMOLED screen and the Nokia Pure font. Designed and
written by Claude (Anthropic) together with smyhu.

- About 160 currencies plus popular cryptocurrencies (BTC, ETH, USDT, BNB, SOL, XRP, USDC, ADA,
  DOGE, LTC). Flat flags.
- Favourites with live conversion: tap a row to make it the base currency, press and hold to
  move or remove it.
- Add currencies from a list with the N9 letter scroller. Search by name, ISO code or symbol
  (e.g. `zł`, `PLN`, `złoty`), in any of the six languages.
- Rates in the Events (Feed) screen; tapping the entry opens the app.
- Background refresh every 1, 3, 6, 12 or 24 hours, also when the app is closed. It only
  downloads when the phone is already online.
- Polish, English, German, Spanish, Italian and French, following the phone language.
  Any other language falls back to English.
- HTTPS first, plain HTTP as a fallback, so it keeps working whichever one a server or the phone
  stops supporting.

Rate sources: [ExchangeRate-API](https://open.er-api.com) (fiat), [CoinGecko](https://www.coingecko.com)
and Binance public data (crypto).

## Install

Copy `dist/waluty_1.1.8_armel.deb` to the phone, then as root (developer mode):

```
aegis-dpkg -i /tmp/waluty_1.1.8_armel.deb
```

Requirements: PySide, python-dbus and Qt Components, all present on a standard PR1.3 phone.
HTTPS needs the community TLS 1.2 patch (OpenSSL 1.0.2 in `/usr/local`); without it the app
uses plain HTTP.

## How it is built

| Part | What it does |
|---|---|
| `src/main.py` | PySide launcher: QML view, Feed and download helpers, starts the background service |
| `src/qml/` | UI (Harmattan Qt Components), currency data (`data.js`), texts (`strings.js`) |
| `src/tlo.py`, `src/common.py` | background service: refresh, settings database, Feed |
| `src/fetch.py` | plain HTTP download in a helper process |
| `native/` | `waluty-fetch`, the native HTTPS helper (see `native/README.md`) |
| `packaging/` | Debian control files and the upstart job `/etc/init/apps/waluty-tlo.conf` |
| `tools/` | generators for the currency list and flags |

`./build-deb.sh` builds the package into `dist/`.

### N9 pitfalls this app works around

- Python 2.6 carries OpenSSL 0.9.8 and the TLS-patched QtNetwork loads OpenSSL 1.0.x, so HTTPS
  through Qt crashes inside Python. HTTPS goes through the native helper instead.
- `aegis-exec -u user` runs programs as `nobody`, and it drops the script argument of an
  interpreter. Aegis also forbids `setuid()` even for root. The upstart job runs `tlo.py` as
  root, and the script restarts itself as `user` through `devel-su`.
- Jobs in `/etc/init/apps` start a few minutes after boot, once the CPU load drops
  (`load-launcher.sh`).

## Credits and licences

- Waluty itself: MIT (`LICENSE`).
- Flags: [flag-icons](https://github.com/lipis/flag-icons), MIT (`packaging/LICENSE-flag-icons`).
- Crypto icons: [cryptocurrency-icons](https://github.com/spothq/cryptocurrency-icons), CC0.
- Currency names: Unicode CLDR.

---

## Po polsku

Konwerter walut dla Nokii N9 (MeeGo Harmattan PR1.3), napisany w 2026 r. zgodnie z wytycznymi
interfejsu N9, z czarnym motywem pod ekran AMOLED i czcionką Nokia Pure. Zaprojektowany i
napisany przez Claude (Anthropic) wspólnie ze smyhu.

- Około 160 walut i popularne kryptowaluty, płaskie flagi.
- Ulubione waluty z przeliczaniem na żywo.
- Wyszukiwanie po nazwie, kodzie albo symbolu.
- Przewijak z literami, jak w N9.
- Kursy na ekranie Wydarzenia (Feed).
- Odświeżanie w tle co 1–24 h, także przy zamkniętej aplikacji.
- Sześć języków: polski, angielski, niemiecki, hiszpański, włoski i francuski, zależnie od
  języka telefonu.

Instalacja: skopiuj `dist/waluty_1.1.8_armel.deb` do `/tmp` w telefonie i jako root wpisz
`aegis-dpkg -i /tmp/waluty_1.1.8_armel.deb`.

Licencja: MIT (plik `LICENSE`).
