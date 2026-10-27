.pragma library
// UI texts; the language comes from the phone setting (uiLang, set in main.py).
// Columns: pl, en, de, es, it, fr. A missing entry falls back to English.

var texts = {
    "title":        { "pl": "Waluty", "en": "Currencies", "de": "Währungen", "es": "Divisas", "it": "Valute", "fr": "Devises" },
    "addTitle":     { "pl": "Dodaj waluty", "en": "Add currencies", "de": "Währungen hinzufügen", "es": "Añadir divisas", "it": "Aggiungi valute", "fr": "Ajouter des devises" },
    "search":       { "pl": "Szukaj: nazwa, kod lub symbol", "en": "Search: name, code or symbol", "de": "Suche: Name, Code oder Symbol", "es": "Buscar: nombre, código o símbolo", "it": "Cerca: nome, codice o simbolo", "fr": "Rechercher : nom, code ou symbole" },
    "updated":      { "pl": "Kursy z %1", "en": "Rates from %1", "de": "Kurse vom %1", "es": "Tipos del %1", "it": "Cambi del %1", "fr": "Taux du %1" },
    "noRates":      { "pl": "Brak kursów, odśwież", "en": "No rates yet, tap refresh", "de": "Noch keine Kurse, bitte aktualisieren", "es": "Sin tipos, pulsa actualizar", "it": "Nessun cambio, tocca aggiorna", "fr": "Aucun taux, actualisez" },
    "loading":      { "pl": "Pobieram kursy…", "en": "Downloading rates…", "de": "Kurse werden geladen…", "es": "Descargando tipos…", "it": "Scarico i cambi…", "fr": "Téléchargement des taux…" },
    "netError":     { "pl": "Nie udało się pobrać kursów", "en": "Could not download rates", "de": "Kurse konnten nicht geladen werden", "es": "No se pudieron descargar los tipos", "it": "Impossibile scaricare i cambi", "fr": "Impossible de télécharger les taux" },
    "cryptoError":  { "pl": "Brak kursów kryptowalut", "en": "Crypto rates unavailable", "de": "Kryptokurse nicht verfügbar", "es": "Tipos de criptomonedas no disponibles", "it": "Cambi delle criptovalute non disponibili", "fr": "Taux des cryptomonnaies indisponibles" },
    "empty":        { "pl": "Dodaj waluty przyciskiem +", "en": "Tap + to add currencies", "de": "Mit + Währungen hinzufügen", "es": "Pulsa + para añadir divisas", "it": "Tocca + per aggiungere valute", "fr": "Touchez + pour ajouter des devises" },
    "moveUp":       { "pl": "Przesuń w górę", "en": "Move up", "de": "Nach oben", "es": "Subir", "it": "Sposta su", "fr": "Monter" },
    "moveDown":     { "pl": "Przesuń w dół", "en": "Move down", "de": "Nach unten", "es": "Bajar", "it": "Sposta giù", "fr": "Descendre" },
    "remove":       { "pl": "Usuń", "en": "Remove", "de": "Entfernen", "es": "Quitar", "it": "Rimuovi", "fr": "Supprimer" },
    "about":        { "pl": "O programie", "en": "About", "de": "Über", "es": "Acerca de", "it": "Informazioni", "fr": "À propos" },
    "settings":     { "pl": "Ustawienia", "en": "Settings", "de": "Einstellungen", "es": "Ajustes", "it": "Impostazioni", "fr": "Paramètres" },
    "autoRefresh":  { "pl": "Odświeżanie w tle", "en": "Background refresh", "de": "Aktualisierung im Hintergrund", "es": "Actualizar en segundo plano", "it": "Aggiornamento in background", "fr": "Actualisation en arrière-plan" },
    "refreshOff":   { "pl": "Wyłączone", "en": "Off", "de": "Aus", "es": "Desactivado", "it": "Disattivato", "fr": "Désactivée" },
    "refreshEvery": { "pl": "Co %1 h", "en": "Every %1 h", "de": "Alle %1 Std.", "es": "Cada %1 h", "it": "Ogni %1 h", "fr": "Toutes les %1 h" },
    "refreshHint":  { "pl": "Kursy i wpis w Feedzie odświeżają się same, także gdy aplikacja jest zamknięta. Potrzebne jest połączenie z internetem.",
                      "en": "Rates and the Feed entry update by themselves, even when the app is closed. An internet connection is needed.",
                      "de": "Kurse und der Feed-Eintrag werden automatisch aktualisiert, auch wenn die App geschlossen ist. Eine Internetverbindung ist nötig.",
                      "es": "Los tipos y la entrada del Feed se actualizan solos, también con la aplicación cerrada. Se necesita conexión a internet.",
                      "it": "I cambi e la voce nel Feed si aggiornano da soli, anche ad app chiusa. Serve una connessione a internet.",
                      "fr": "Les taux et l'entrée du Feed se mettent à jour seuls, même application fermée. Une connexion internet est nécessaire." },
    "showInFeed":   { "pl": "Kursy w Feedzie", "en": "Rates in Feed", "de": "Kurse im Feed", "es": "Tipos en el Feed", "it": "Cambi nel Feed", "fr": "Taux dans le Feed" },
    "feedTitle":    { "pl": "Kursy walut", "en": "Exchange rates", "de": "Wechselkurse", "es": "Tipos de cambio", "it": "Tassi di cambio", "fr": "Taux de change" },
    "aboutText":    { "pl": "Zaprojektowany i napisany przez Claude (Anthropic) wspólnie ze smyhu dla Nokii N9.\n\nKursy: ExchangeRate-API (open.er-api.com), kryptowaluty: CoinGecko i Binance.\nFlagi: flag-icons (MIT), ikony kryptowalut: cryptocurrency-icons (CC0).",
                      "en": "Designed and written by Claude (Anthropic) together with smyhu for the Nokia N9.\n\nRates: ExchangeRate-API (open.er-api.com), cryptocurrencies: CoinGecko and Binance.\nFlags: flag-icons (MIT), crypto icons: cryptocurrency-icons (CC0).",
                      "de": "Entworfen und geschrieben von Claude (Anthropic) gemeinsam mit smyhu für das Nokia N9.\n\nKurse: ExchangeRate-API (open.er-api.com), Kryptowährungen: CoinGecko und Binance.\nFlaggen: flag-icons (MIT), Krypto-Symbole: cryptocurrency-icons (CC0).",
                      "es": "Diseñada y escrita por Claude (Anthropic) junto con smyhu para el Nokia N9.\n\nTipos de cambio: ExchangeRate-API (open.er-api.com), criptomonedas: CoinGecko y Binance.\nBanderas: flag-icons (MIT), iconos de criptomonedas: cryptocurrency-icons (CC0).",
                      "it": "Progettata e scritta da Claude (Anthropic) insieme a smyhu per il Nokia N9.\n\nCambi: ExchangeRate-API (open.er-api.com), criptovalute: CoinGecko e Binance.\nBandiere: flag-icons (MIT), icone delle criptovalute: cryptocurrency-icons (CC0).",
                      "fr": "Conçue et écrite par Claude (Anthropic) avec smyhu pour le Nokia N9.\n\nTaux : ExchangeRate-API (open.er-api.com), cryptomonnaies : CoinGecko et Binance.\nDrapeaux : flag-icons (MIT), icônes crypto : cryptocurrency-icons (CC0)." },
    "close":        { "pl": "Zamknij", "en": "Close", "de": "Schließen", "es": "Cerrar", "it": "Chiudi", "fr": "Fermer" }
};

function t(lang, key)
{
    var entry = texts[key];
    if (!entry)
        return key;
    return entry[lang] !== undefined ? entry[lang] : entry["en"];
}
