# Appends popular cryptocurrencies (CoinGecko ids, CC0 icons) to currencies.js
import json, os, sys, cairosvg
OUT, ICONS = sys.argv[1], sys.argv[2]
coins = [('BTC', 'bitcoin', 'Bitcoin', '₿'), ('ETH', 'ethereum', 'Ethereum', 'Ξ'),
         ('USDT', 'tether', 'Tether', ''), ('BNB', 'binancecoin', 'BNB', ''),
         ('SOL', 'solana', 'Solana', ''), ('XRP', 'ripple', 'XRP', ''),
         ('USDC', 'usd-coin', 'USD Coin', ''), ('ADA', 'cardano', 'Cardano', ''),
         ('DOGE', 'dogecoin', 'Dogecoin', 'Ð'), ('LTC', 'litecoin', 'Litecoin', 'Ł')]
path = os.path.join(OUT, 'currencies.js')
src = open(path, encoding='utf-8').read()
head, data = src.split('var list = ', 1)
lst = json.loads(data.rstrip().rstrip(';'))
for code, cg, name, sym in coins:
    flag = 'c-' + code.lower()
    svg = open(os.path.join(ICONS, code.lower() + '.svg'), encoding='utf-8').read()
    # center the round 32x32 icon in a 60x45 canvas, like the flags
    wrapped = ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
               'width="60" height="45"><svg x="7.5" y="0" width="45" height="45" viewBox="0 0 32 32">'
               + svg.split('>', 1)[1])
    wrapped = wrapped.rsplit('</svg>', 1)[0] + '</svg></svg>'
    cairosvg.svg2png(bytestring=wrapped.encode(), write_to=os.path.join(OUT, 'flags', flag + '.png'))
    lst.append({'code': code, 'en': name, 'pl': name, 'sym': sym, 'flag': flag, 'cg': cg})
with open(path, 'w', encoding='utf-8') as f:
    f.write(head + 'var list = ' + json.dumps(lst, ensure_ascii=False).replace('}, {', '},\n{') + ';\n')
print(len(lst))
