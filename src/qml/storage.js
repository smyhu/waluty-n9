// Settings and cached rates in the QML offline storage (SQLite)

function db()
{
    var d = openDatabaseSync("waluty", "1.0", "Waluty", 200000);
    d.transaction(function(tx) {
        tx.executeSql("CREATE TABLE IF NOT EXISTS settings(key TEXT UNIQUE, value TEXT)");
    });
    return d;
}

function get(key, fallback)
{
    var value = fallback;
    db().readTransaction(function(tx) {
        var rs = tx.executeSql("SELECT value FROM settings WHERE key = ?", [key]);
        if (rs.rows.length > 0)
            value = rs.rows.item(0).value;
    });
    return value;
}

function set(key, value)
{
    db().transaction(function(tx) {
        tx.executeSql("INSERT OR REPLACE INTO settings VALUES(?, ?)", [key, String(value)]);
    });
}
