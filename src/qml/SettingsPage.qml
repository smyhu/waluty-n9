import QtQuick 1.1
import com.nokia.meego 1.0
import "storage.js" as Store
import "strings.js" as S

// Settings: background refresh interval and the Feed entry.
// The background service (tlo.py) reads the same keys from the database.
Page {
    id: settingsPage

    property variant hours: [0, 1, 3, 6, 12, 24]
    property int interval: parseInt(Store.get("interval", "3"))

    orientationLock: PageOrientation.LockPortrait

    function tr(key) { return S.t(uiLang, key) }

    function label(h)
    {
        return h == 0 ? tr("refreshOff") : tr("refreshEvery").replace("%1", h);
    }

    function choices()
    {
        var out = [];
        for (var i = 0; i < hours.length; ++i)
            out.push(label(hours[i]));
        return out;
    }

    Header {
        id: header
        anchors.top: parent.top
        text: tr("settings")
    }

    Column {
        anchors.top: header.bottom
        anchors.topMargin: 16
        anchors.left: parent.left
        anchors.right: parent.right

        // background refresh: tap opens the list of intervals
        Item {
            width: parent.width
            height: 88

            Rectangle {
                anchors.fill: parent
                color: refreshMouse.pressed ? "#1A3A5A" : "black"
            }
            Column {
                anchors.left: parent.left
                anchors.leftMargin: 16
                anchors.verticalCenter: parent.verticalCenter
                Text {
                    font.family: "Nokia Pure Text"
                    font.pixelSize: 26
                    font.bold: true
                    color: "white"
                    text: tr("autoRefresh")
                }
                Text {
                    font.family: "Nokia Pure Text"
                    font.pixelSize: 22
                    color: "#3D9BE9"
                    text: label(settingsPage.interval)
                }
            }
            MouseArea {
                id: refreshMouse
                anchors.fill: parent
                onClicked: {
                    var sel = 0;
                    for (var i = 0; i < hours.length; ++i)
                        if (hours[i] == settingsPage.interval)
                            sel = i;
                    intervalDialog.selectedIndex = sel;
                    intervalDialog.open();
                }
            }
        }

        Text {
            x: 16
            width: parent.width - 32
            wrapMode: Text.WordWrap
            font.family: "Nokia Pure Text"
            font.pixelSize: 20
            color: "#8C8C8C"
            text: tr("refreshHint")
        }

        Item { width: 1; height: 24 }

        Rectangle { x: 16; width: parent.width - 32; height: 1; color: "#333333" }

        // Feed entry on/off
        Item {
            width: parent.width
            height: 88

            Text {
                anchors.left: parent.left
                anchors.leftMargin: 16
                anchors.verticalCenter: parent.verticalCenter
                font.family: "Nokia Pure Text"
                font.pixelSize: 26
                font.bold: true
                color: "white"
                text: tr("showInFeed")
            }
            Switch {
                id: feedSwitch
                anchors.right: parent.right
                anchors.rightMargin: 16
                anchors.verticalCenter: parent.verticalCenter
                checked: Store.get("feed", "1") == "1"
                onCheckedChanged: {
                    var value = checked ? "1" : "0";
                    if (value == Store.get("feed", "1"))
                        return;
                    Store.set("feed", value);
                    if (checked && mainPageRef)
                        mainPageRef.publishFeed();
                    else
                        feed.clear();
                }
            }
        }
    }

    property Item mainPageRef

    SelectionDialog {
        id: intervalDialog
        titleText: tr("autoRefresh")
        model: settingsPage.choices()
        onAccepted: {
            settingsPage.interval = hours[selectedIndex];
            Store.set("interval", settingsPage.interval);
            service.wake();
        }
    }

    tools: ToolBarLayout {
        ToolIcon {
            platformIconId: "toolbar-back"
            onClicked: pageStack.pop()
        }
    }
}
