/*
 * Copyright 2012-2013 Canonical Ltd.
 *
 * This file is part of dialer-app.
 *
 * dialer-app is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; version 3.
 *
 * dialer-app is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

import QtQuick 2.0
import Ubuntu.Components 0.1
import Ubuntu.Telephony 0.1

Column {
    id: multiCallArea

    property variant calls: null

    spacing: units.gu(1)
    visible: opacity > 0

    Behavior on opacity {
        UbuntuNumberAnimation { }
    }

    Repeater {
        id: multiCallRepeater
        model: multiCallArea.calls

        Item {
            id: callDelegate
            property QtObject callEntry: modelData
            property bool isLast: index == (multiCallRepeater.count - 1)

            height: backgroundRect.height + (isLast ? 0 : mergeButton.height + units.gu(1))
            anchors {
                left: parent.left
                right: parent.right
            }

            Image {
                id: avatar
                anchors.fill: backgroundRect
                source: watcher.avatar
                fillMode: Image.PreserveAspectCrop
                smooth: true

                Rectangle {
                    anchors {
                        left: parent.left
                        top: parent.top
                        right: parent.right
                    }
                    height: units.gu(8)
                    color: "black"
                    opacity: avatar.status == Image.Ready && !callEntry.held ? 0.4 : 0
                    Behavior on opacity {
                        UbuntuNumberAnimation { }
                    }
                }
            }

            Rectangle {
                id: backgroundRect
                color: {
                    if (callEntry.held) {
                        return "black";
                    } else if (avatar.status == Image.Null) {
                        return "white";
                    } else {
                        return "transparent"
                    }
                }

                opacity: 0.5
                height: (multiCallArea.height - units.gu(7)) / (multiCallRepeater.count > 0 ? multiCallRepeater.count : 1)
                anchors {
                    left: parent.left
                    right: parent.right
                    top: parent.top
                }

                Behavior on color {
                    ColorAnimation {
                        duration: 150
                    }
                }
            }

            ContactWatcher {
                id: watcher
                phoneNumber: callEntry.phoneNumber
            }

            Label {
                id: aliasLabel
                fontSize: "large"
                anchors {
                    left: parent.left
                    top: parent.top
                    margins: units.gu(1)
                }
                text: {
                    if (callEntry.isConference) {
                        return i18n.tr("Conference");
                    } else if (callEntry.voicemail) {
                        return i18n.tr("Voicemail");
                    } else if (watcher.alias != "") {
                        return watcher.alias;
                    } else {
                        return watcher.phoneNumber;
                    }
                }
            }

            Label {
                fontSize: "medium"
                anchors {
                    left: parent.left
                    top: aliasLabel.bottom
                    margins: units.gu(1)
                }
                text: callEntry.held ? i18n.tr("on hold") : i18n.tr("active")
            }

            MouseArea {
                anchors.fill: backgroundRect
                onClicked: callEntry.held = false;
                enabled: callEntry.held
            }

            LiveCallKeypadButton {
                id: participantsButton
                visible: callEntry.isConference
                iconSource: "navigation-menu"
                iconWidth: units.gu(3)
                iconHeight: units.gu(3)
                width: visible ? units.gu(6) : 0
                height: units.gu(6)
                anchors {
                    verticalCenter: backgroundRect.verticalCenter
                    right: parent.right
                    rightMargin: units.gu(1)
                }
                onClicked: conferenceCallArea.conference = callEntry
            }

            Button {
                id: mergeButton
                visible: !isLast
                anchors {
                    bottom: parent.bottom
                    horizontalCenter: parent.horizontalCenter
                }

                text: i18n.tr("Merge calls")
                onClicked: {
                    callManager.mergeCalls(callManager.calls[index], callManager.calls[index+1])
                }
            }
        }
    }
}