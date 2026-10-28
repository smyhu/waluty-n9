import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.1
import "data.js" as Data
import "net.js" as Net
import "storage.js" as Store
import "strings.js" as S

Page {
    id: mainPage

    property string base: Store.get("base", "USD")
    property real amount: parseFloat(Store.get("amount", "100"))
    property variant rates: ({})
    property string infoText: ""
    property bool busy: false
    property int menuIndex: -1

    orientationLock: PageOrientation.LockPortrait

    function tr(key) { return S.t(uiLang, key) }

    function favourites()
    {
        var s = Store.get("favourites", "USD,EUR,GBP,PLN,BTC");
        return s == "" ? [] : s.split(",");
    }

    function saveFavourites()
    {
        var codes = [];
        for (var i = 0; i < favModel.count; ++i)
            codes.push(favModel.get(i).code);
        Store.set("favourites", codes.join(","));
    }

    function convert(code)
    {
        var from = rates[base], to = rates[code];
        if (!from || !to)
            return NaN;
        return amount / from * to;
    }

    function rebuild()
    {
        var codes = favourites();
        favModel.clear();
        for (var i = 0; i < codes.length; ++i) {
            var c = Data.info(codes[i]);
            if (!c)
                continue;
            favModel.append({ "code": c.code, "name": Data.nameOf(c, uiLang),
                              "sym": c.sym, "flag": c.flag, "value": "" });
        }
        if (codes.indexOf(base) < 0 && favModel.count > 0)
            base = favModel.get(0).code;
        updateValues();
    }

    function updateValues()
    {
        for (var i = 0; i < favModel.count; ++i) {
            var code = favModel.get(i).code;
            favModel.setProperty(i, "value", Data.format(convert(code), uiLang));
        }
        updateStatus();
    }

    function updateStatus()
    {
        var t = parseInt(Store.get("ratesTime", "0"));
        if (busy)
            infoText = tr("loading");
        else if (t > 0)
            infoText = tr("updated").replace("%1", Qt.formatDateTime(new Date(t), "yyyy-MM-dd hh:mm"));
        else
            infoText = tr("noRates");
    }

    function loadCachedRates()
    {
        try { rates = JSON.parse(Store.get("rates", "{}")); } catch (e) { rates = {}; }
    }

    function refresh(force)
    {
        var age = new Date().getTime() - parseInt(Store.get("ratesTime", "0"));
        if (!force && age < 3600000)
            return;
        busy = true;
        updateStatus();
        console.log("waluty: downloading rates");
        Net.fetchFiat(function(fiat) {
            console.log("waluty: fiat " + (fiat ? "ok" : "failed"));
            Net.fetchCrypto(Data.list, function(crypto) {
                console.log("waluty: crypto " + (crypto ? "ok" : "failed"));
                busy = false;
                if (!fiat) {
                    updateStatus();
                    errorBanner.text = tr("netError");
                    errorBanner.show();
                    return;
                }
                var merged = {};
                for (var k in fiat) merged[k] = fiat[k];
                var old = rates;
                if (crypto) {
                    for (var c in crypto) merged[c] = crypto[c];
                } else {
                    for (var o in old) if (merged[o] === undefined) merged[o] = old[o];
                    errorBanner.text = tr("cryptoError");
                    errorBanner.show();
                }
                rates = merged;
                Store.set("rates", JSON.stringify(merged));
                Store.set("ratesTime", new Date().getTime());
                loadedTime = Store.get("ratesTime", "0");
                updateValues();
                publishFeed();
            });
        });
    }

    function publishFeed()
    {
        if (Store.get("feed", "1") != "1")
            return;
        var lines = [];
        for (var i = 0; i < favModel.count && lines.length < 4; ++i) {
            var code = favModel.get(i).code;
            if (code == base || !rates[code] || !rates[base])
                continue;
            lines.push("1 " + code + " = " + Data.format(rates[base] / rates[code], uiLang) + " " + base);
        }
        if (lines.length > 0)
            feed.publish(tr("feedTitle"), lines.join("   ·   "));
    }

    function makeBase(index)
    {
        var item = favModel.get(index);
        var v = convert(item.code);
        base = item.code;
        if (!isNaN(v))
            amount = Math.round(v * 100) / 100;
        Store.set("base", base);
        Store.set("amount", amount);
        amountField.text = Data.plainNumber(amount, uiLang);
        updateValues();
    }

    Connections {
        target: downloader
        onDone: Net.dispatch()
    }

    Component.onCompleted: {
        loadCachedRates();
        rebuild();
        amountField.text = Data.plainNumber(amount, uiLang);
        console.log("waluty: main page ready");
        if (!noNet)
            refresh(false);
    }

    onStatusChanged: {
        // back from the picker: show the new favourites
        if (status == PageStatus.Activating) {
            reloadIfNewer();
            rebuild();
        }
    }

    ListModel { id: favModel }

    // the background service (tlo.py) may have stored newer rates meanwhile
    property string loadedTime: Store.get("ratesTime", "0")
    function reloadIfNewer()
    {
        var t = Store.get("ratesTime", "0");
        if (busy || t == loadedTime)
            return;
        loadedTime = t;
        loadCachedRates();
        updateValues();
    }

    Timer {
        interval: 60000
        repeat: true
        running: Qt.application.active
        onTriggered: reloadIfNewer()
    }

    Header {
        id: header
        anchors.top: parent.top
        text: tr("title")
        subText: mainPage.infoText
    }

    // amount entry for the selected (base) currency
    Rectangle {
        id: entry
        anchors.top: header.bottom
        width: parent.width
        height: 96
        color: "black"

        Image {
            id: baseFlag
            anchors.left: parent.left
            anchors.leftMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            source: Data.info(base) ? "flags/" + Data.info(base).flag + ".png" : ""
        }
        Text {
            id: baseCode
            anchors.left: baseFlag.right
            anchors.leftMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            font.family: "Nokia Pure Text"
            font.pixelSize: 28
            font.bold: true
            color: "white"
            text: base
        }
        TextField {
            id: amountField
            anchors.left: baseCode.right
            anchors.leftMargin: 16
            anchors.right: parent.right
            anchors.rightMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            inputMethodHints: Qt.ImhFormattedNumbersOnly | Qt.ImhNoPredictiveText
            onTextChanged: {
                mainPage.amount = Data.parseAmount(text);
                Store.set("amount", mainPage.amount);
                updateValues();
            }
        }
        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: "#333333"
        }
    }

    ListView {
        id: favList
        anchors.top: entry.bottom
        anchors.bottom: parent.bottom
        width: parent.width
        clip: true
        model: favModel

        delegate: Item {
            id: row
            width: favList.width
            height: 88

            Rectangle {
                anchors.fill: parent
                color: mouse.pressed ? "#1A3A5A" : (code == mainPage.base ? "#101820" : "black")
            }
            Rectangle {
                visible: code == mainPage.base
                width: 4
                height: parent.height
                color: "#3D9BE9"
            }
            Image {
                id: flagImage
                anchors.left: parent.left
                anchors.leftMargin: 16
                anchors.verticalCenter: parent.verticalCenter
                source: "flags/" + flag + ".png"
            }
            Column {
                anchors.left: flagImage.right
                anchors.leftMargin: 16
                anchors.right: valueText.left
                anchors.rightMargin: 8
                anchors.verticalCenter: parent.verticalCenter
                Text {
                    font.family: "Nokia Pure Text"
                    font.pixelSize: 28
                    font.bold: true
                    color: "white"
                    text: code + (sym != "" ? "  " + sym : "")
                }
                Text {
                    width: parent.width
                    font.family: "Nokia Pure Text"
                    font.pixelSize: 20
                    color: "#8C8C8C"
                    elide: Text.ElideRight
                    text: name
                }
            }
            Text {
                id: valueText
                anchors.right: parent.right
                anchors.rightMargin: 16
                anchors.verticalCenter: parent.verticalCenter
                font.family: "Nokia Pure Text Light"
                font.pixelSize: 32
                color: "white"
                text: value === undefined ? "" : value
            }
            Rectangle {
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.leftMargin: 16
                anchors.right: parent.right
                height: 1
                color: "#222222"
            }
            MouseArea {
                id: mouse
                anchors.fill: parent
                onClicked: makeBase(index)
                onPressAndHold: {
                    mainPage.menuIndex = index;
                    rowMenu.open();
                }
            }
        }
    }

    ScrollDecorator { flickableItem: favList }

    Text {
        anchors.centerIn: favList
        visible: favModel.count == 0
        font.family: "Nokia Pure Text Light"
        font.pixelSize: 28
        color: "#8C8C8C"
        text: tr("empty")
    }

    InfoBanner { id: errorBanner }

    ContextMenu {
        id: rowMenu
        MenuLayout {
            MenuItem {
                text: tr("moveUp")
                enabled: mainPage.menuIndex > 0
                onClicked: { favModel.move(mainPage.menuIndex, mainPage.menuIndex - 1, 1); saveFavourites(); }
            }
            MenuItem {
                text: tr("moveDown")
                enabled: mainPage.menuIndex >= 0 && mainPage.menuIndex < favModel.count - 1
                onClicked: { favModel.move(mainPage.menuIndex, mainPage.menuIndex + 1, 1); saveFavourites(); }
            }
            MenuItem {
                text: tr("remove")
                onClicked: {
                    favModel.remove(mainPage.menuIndex);
                    saveFavourites();
                    if (favModel.count > 0 && favourites().indexOf(mainPage.base) < 0)
                        makeBase(0);
                }
            }
        }
    }

    Menu {
        id: mainMenu
        MenuLayout {
            MenuItem {
                text: tr("settings")
                onClicked: pageStack.push(Qt.resolvedUrl("SettingsPage.qml"), { mainPageRef: mainPage })
            }
            MenuItem {
                text: tr("about")
                onClicked: aboutDialog.open()
            }
        }
    }

    QueryDialog {
        id: aboutDialog
        icon: "file:///usr/share/icons/hicolor/80x80/apps/waluty80.png"
        titleText: tr("title") + " 1.1.7"
        message: tr("aboutText")
        acceptButtonText: tr("close")
    }

    tools: ToolBarLayout {
        ToolIcon {
            platformIconId: "toolbar-add"
            onClicked: pageStack.push(Qt.resolvedUrl("PickerPage.qml"))
        }
        ToolIcon {
            platformIconId: "toolbar-refresh"
            enabled: !mainPage.busy
            onClicked: refresh(true)
        }
        ToolIcon {
            platformIconId: "toolbar-view-menu"
            onClicked: (mainMenu.status == DialogStatus.Closed) ? mainMenu.open() : mainMenu.close()
        }
    }
}
