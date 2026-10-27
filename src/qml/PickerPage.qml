import QtQuick 1.1
import com.nokia.meego 1.0
import "data.js" as Data
import "storage.js" as Store
import "strings.js" as S

Page {
    id: pickerPage

    property variant favs: ({})

    orientationLock: PageOrientation.LockPortrait

    function tr(key) { return S.t(uiLang, key) }

    function loadFavs()
    {
        var s = Store.get("favourites", "USD,EUR,GBP,PLN,BTC");
        var m = {};
        var codes = s == "" ? [] : s.split(",");
        for (var i = 0; i < codes.length; ++i)
            m[codes[i]] = true;
        favs = m;
    }

    function fill(query)
    {
        var all = Data.sortedFor(uiLang);
        listModel.clear();
        for (var i = 0; i < all.length; ++i) {
            var c = all[i];
            if (!Data.matches(c, query))
                continue;
            listModel.append({ "code": c.code, "name": Data.nameOf(c, uiLang), "sym": c.sym,
                               "flag": c.flag, "letter": Data.letterOf(c, uiLang),
                               "chosen": favs[c.code] === true });
        }
    }

    function toggle(index)
    {
        var item = listModel.get(index);
        var s = Store.get("favourites", "USD,EUR,GBP,PLN,BTC");
        var codes = s == "" ? [] : s.split(",");
        var pos = codes.indexOf(item.code);
        if (pos >= 0)
            codes.splice(pos, 1);
        else
            codes.push(item.code);
        Store.set("favourites", codes.join(","));
        listModel.setProperty(index, "chosen", pos < 0);
        loadFavs();
    }

    Component.onCompleted: {
        loadFavs();
        fill("");
    }

    ListModel { id: listModel }

    Header {
        id: header
        anchors.top: parent.top
        text: tr("addTitle")
    }

    TextField {
        id: searchField
        anchors.top: header.bottom
        anchors.topMargin: 12
        anchors.left: parent.left
        anchors.leftMargin: 16
        anchors.right: parent.right
        anchors.rightMargin: 16
        placeholderText: tr("search")
        inputMethodHints: Qt.ImhNoPredictiveText
        onTextChanged: fill(text)
    }

    ListView {
        id: list
        anchors.top: searchField.bottom
        anchors.topMargin: 12
        anchors.bottom: parent.bottom
        width: parent.width
        clip: true
        model: listModel
        // sections feed the letter bubble of the SectionScroller; no header rows
        section.property: "letter"
        section.criteria: ViewSection.FullString

        delegate: Item {
            width: list.width
            height: 80

            Rectangle {
                anchors.fill: parent
                color: mouse.pressed ? "#1A3A5A" : "black"
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
                anchors.right: check.left
                anchors.rightMargin: 8
                anchors.verticalCenter: parent.verticalCenter
                Text {
                    width: parent.width
                    font.family: "Nokia Pure Text"
                    font.pixelSize: 26
                    color: chosen ? "#3D9BE9" : "white"
                    elide: Text.ElideRight
                    text: name
                }
                Text {
                    font.family: "Nokia Pure Text"
                    font.pixelSize: 20
                    color: "#8C8C8C"
                    text: code + (sym != "" ? "  ·  " + sym : "")
                }
            }
            Image {
                id: check
                anchors.right: parent.right
                anchors.rightMargin: 40   // keep clear of the section scroller
                anchors.verticalCenter: parent.verticalCenter
                source: "check.png"
                visible: chosen
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
                onClicked: toggle(index)
            }
        }
    }

    SectionScroller { listView: list }

    tools: ToolBarLayout {
        ToolIcon {
            platformIconId: "toolbar-back"
            onClicked: pageStack.pop()
        }
    }
}
