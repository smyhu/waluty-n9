// Rate downloads. Deliberately not a .pragma library: in Qt 4.7 an
// XMLHttpRequest started from a shared library script has no QML context.

// Downloads run in Python (downloader, see main.py): HTTPS first, plain HTTP
// as fallback, each attempt in a helper process so an SSL crash can't take
// the app down. XMLHttpRequest crashed the app on the N9 (versions 1.0.2-1.0.3).
var pending = {};
var counter = 0;

function getJson(urls, done)
{
    var tag = "r" + (++counter);
    pending[tag] = done;
    downloader.get(tag, urls.join(" "));
}

// called from MainPage when downloader signals done
function dispatch()
{
    var raw;
    while ((raw = downloader.take()) != "") {
        var r = JSON.parse(raw);
        var cb = pending[r.tag];
        delete pending[r.tag];
        var obj = null;
        if (r.ok) {
            try { obj = JSON.parse(r.text); } catch (e) { obj = null; }
        }
        if (cb)
            cb(obj);
    }
}

// rates: {CODE: units per 1 USD}
function fetchFiat(done)
{
    getJson(["https://open.er-api.com/v6/latest/USD", "http://open.er-api.com/v6/latest/USD"],
            function(obj) {
                done(obj && obj.result == "success" ? obj.rates : null);
            });
}

// Crypto: CoinGecko (HTTPS only), then Binance's public data mirror, which
// still answers over plain HTTP. Binance prices are in USDT; USDT itself is
// taken from the USDC/USDT pair and USDC is treated as 1 USD.
var binancePairs = { BTC: "BTCUSDT", ETH: "ETHUSDT", BNB: "BNBUSDT", SOL: "SOLUSDT",
                     XRP: "XRPUSDT", ADA: "ADAUSDT", DOGE: "DOGEUSDT", LTC: "LTCUSDT",
                     USDC: "USDCUSDT" };

function fetchCrypto(coins, done)
{
    var ids = [];
    for (var j = 0; j < coins.length; ++j)
        if (coins[j].cg)
            ids.push(coins[j].cg);
    var q = "/api/v3/simple/price?vs_currencies=usd&ids=" + ids.join(",");
    getJson(["https://api.coingecko.com" + q], function(obj) {
        if (obj) {
            var rates = {};
            for (var i = 0; i < coins.length; ++i) {
                var c = coins[i];
                if (c.cg && obj[c.cg] && obj[c.cg].usd > 0)
                    rates[c.code] = 1 / obj[c.cg].usd;
            }
            done(rates);
            return;
        }
        fetchCryptoBinance(done);
    });
}

function fetchCryptoBinance(done)
{
    var syms = [];
    for (var k in binancePairs)
        syms.push('%22' + binancePairs[k] + '%22');
    var path = "/api/v3/ticker/price?symbols=%5B" + syms.join(",") + "%5D";
    getJson(["https://data-api.binance.vision" + path, "http://data-api.binance.vision" + path],
            function(list) {
        if (!list || !list.length) {
            done(null);
            return;
        }
        var price = {};
        for (var i = 0; i < list.length; ++i)
            price[list[i].symbol] = parseFloat(list[i].price);
        var usdt = price["USDCUSDT"] > 0 ? price["USDCUSDT"] : 1;   // USDT per 1 USD
        var rates = { USDT: usdt, USDC: 1 };
        for (var code in binancePairs) {
            var p = price[binancePairs[code]];
            if (code != "USDC" && p > 0)
                rates[code] = usdt / p;
        }
        done(rates);
    });
}
