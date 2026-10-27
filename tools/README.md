# Data generators

- `dane.py` builds the fiat currency list (ISO code, CLDR names, symbol, flag file) and renders the
  flags from [flag-icons](https://github.com/lipis/flag-icons) to 60x45 PNG (needs `babel`, `cairosvg`).
- `krypto.py` appends the cryptocurrencies and renders their icons from
  [cryptocurrency-icons](https://github.com/spothq/cryptocurrency-icons).

The German, Spanish, Italian and French names in `src/qml/data.js` were added afterwards from
CLDR (Babel), plus 8 names written by hand where CLDR has none.
