import re

from PyQt5 import QtWidgets, QtCore, QtGui

from ..utils.styles import get_font, colors, entry_style, list_style, main_frame_style
from ..utils.widgets import Entry

USERNAME = "<not-initialized>"


class Room(QtWidgets.QWidget):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.online = []

        self.name_label = QtWidgets.QLabel(self.name, self)
        self.name_label.setFont(get_font(18, False, "Lato Black"))
        self.name_label.setStyleSheet(f"color: {colors['black']};"
                                      f"background-color: transparent;"
                                      f"border: none;")
        self.name_label.move(75, 15)
        self.name_label.adjustSize()

        self.online_label = QtWidgets.QLabel("", self)
        self.online_label.setFont(get_font(16, False, "Lato"))
        self.online_label.setStyleSheet(f"color: {colors['black']};"
                                        f"background-color: transparent;"
                                        f"border: none;")
        self.online_label.move(75, 40)
        self.online_label.adjustSize()

        self.img = QtWidgets.QLabel(parent=self)
        self.img.setPixmap(QtGui.QPixmap(f'images/{self.name}.png').scaled(50, 50))
        self.img.setStyleSheet("background-color: white; border-radius: 25")
        self.img.setGeometry(10, 10, 50, 50)

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(max(self.online_label.width(), self.name_label.width()) + 100, 70)

    def update_online(self):
        users = [username if username != USERNAME else 'You' for username in self.online]
        if len(users) == 0:
            online = ""
        elif len(users) == 1:
            online = users[0]
        else:
            online = ", ".join(users[:-1]) + f" & {users[-1]}"
        self.online_label.setText(online)
        self.online_label.adjustSize()


class Message(QtWidgets.QWidget):
    def __init__(self, text, author_name, author_username, line_length, side):
        super(Message, self).__init__()

        self.text = text

        self.frame = QtWidgets.QFrame(self)
        self.frame.setMinimumWidth(20)
        color = {'left': 'rgba(253, 255, 182, 200)', 'right': 'white', 'center': 'rgba(0, 0, 0, 50)'}
        self.frame.setStyleSheet(f"border-radius: {10 if side != 'center' else 12}px;"
                                 f"background-color: {color[side]}")

        self.text_edit = QtWidgets.QTextEdit(self.frame)
        self.text_edit.setStyleSheet(f"color: {colors['black'] if side != 'center' else 'white'};"
                                     f"background-color: transparent;"
                                     f"border: none;")
        self.text_edit.setFont(get_font(16, False))
        self.text_edit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.text_edit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.text_edit.setReadOnly(True)
        self.text_edit.move(0, 0)
        self.text_edit.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        if side == "right":
            text = text.replace('\n', '<br>')
            self.text_edit.insertHtml(
                f"<p style=\"font-size:14px;\"><b>{author_username}</b> ● {author_name}</p><p>{text}</p>")
        else:
            self.text_edit.insertPlainText(text)
        self.resize_message(line_length)

    def sizeHint(self) -> QtCore.QSize:
        return self.frame.size()

    def resize_message(self, size):
        self.text_edit.document().setTextWidth(size)
        self.text_edit.resize(self.text_edit.document().idealWidth(), self.text_edit.document().size().height())
        self.text_edit.document().setTextWidth(self.text_edit.width())
        self.frame.adjustSize()
        self.adjustSize()


class MessageItem(QtWidgets.QWidget):
    def __init__(self, text, author_name, author_username, line_length, side):
        super(MessageItem, self).__init__()

        self.side = side
        self.item = None

        self.setStyleSheet("border: none;")

        self.msg = Message(text, author_name, author_username, line_length, side)
        self.msg.setParent(self)

        self.move_msg()

    def move_msg(self):
        if self.side == "left":
            self.msg.move(5, 5)
        elif self.side == "center":
            self.msg.move((self.width() - self.msg.width()) // 2, (self.height() - self.msg.height()) // 2)
        elif self.side == "right":
            self.msg.move(self.width() - self.msg.width() - 5, 5)
        else:
            raise Exception("Unsupported side")

    def width(self) -> int:
        w = super().width()

        if self.item and self.item.listWidget().verticalScrollBar().isVisible():
            w -= self.item.listWidget().verticalScrollBar().width()

        return w

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.msg.resize_message(self.item.listWidget().width() * 2 // 3)
        self.resize(self.item.listWidget().width(), self.msg.height() + 10)
        self.move_msg()


class MessageList(QtWidgets.QListWidget):
    def __init__(self, parent):
        super(MessageList, self).__init__(parent)

        self.setStyleSheet(
                f"background-color: transparent;"
                f"border: 1px solid;"
                f"border-color: {colors['gray']} none none none;"
                f"outline: none;")
        self.setSelectionMode(QtWidgets.QListWidget.NoSelection)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

    def add_message(self, *, text, author_name="", author_username="", side):
        message = MessageItem(text=text, author_name=author_name, author_username=author_username, side=side,
                              line_length=self.width() // 2)
        item = QtWidgets.QListWidgetItem(self)
        self.addItem(item)
        message.item = item
        item.setSizeHint(message.size())
        self.setItemWidget(item, message)
        self.scrollToBottom()
        self.resizeEvent(QtGui.QResizeEvent(self.size(), self.size()))

    def resizeEvent(self, e: QtGui.QResizeEvent) -> None:
        super(MessageList, self).resizeEvent(e)

        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if widget is None:
                continue
            widget.resizeEvent(e)
            item.setSizeHint(widget.size())


class Chat(QtWidgets.QMainWindow):
    def __init__(self, client):
        super(Chat, self).__init__()

        self.client = client
        global USERNAME
        USERNAME = client.username

        self.setWindowTitle("Chat Application")
        self.setFocusPolicy(QtCore.Qt.ClickFocus)

        self.contacts_frame = QtWidgets.QFrame(self)
        self.contacts_frame.setGeometry(0, 0, 300, 800)
        self.contacts_frame.setStyleSheet(f"background-color: white;")
        self.contacts_frame.setMinimumWidth(300)

        self.chat_frame = QtWidgets.QFrame(self)
        self.chat_frame.setGeometry(300, 0, 900, 800)
        self.chat_frame.setObjectName("frame")
        self.chat_frame.setStyleSheet(main_frame_style)

        self.typing_area = QtWidgets.QFrame(self.chat_frame)
        self.typing_area.setGeometry(0, 760, 900, 40)
        self.typing_area.setStyleSheet("background-color: white")

        self.entry = QtWidgets.QTextEdit(self.typing_area)
        self.entry.setGeometry(0, 0, 900, 40)
        self.entry.setFont(get_font(18, False))
        self.entry.setStyleSheet(f"border: 1px solid;"
                                 f"border-color: {colors['gray']} none none {colors['gray']};")
        self.entry.setFont(get_font(18, False))
        self.entry.setViewportMargins(5, 5, 50, 5)
        self.entry.setAlignment(QtCore.Qt.AlignVCenter)
        self.entry.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.entry.setPlaceholderText("Write a message...")
        self.entry.setAcceptRichText(False)
        self.entry.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.entry.textChanged.connect(self.typing)

        self.current_msg = ""

        self.send_button = QtWidgets.QPushButton(self.typing_area)
        self.send_button.setIcon(QtGui.QIcon("images/send_button.png"))
        self.send_button.resize(QtCore.QSize(40, 40))
        self.send_button.setIconSize(QtCore.QSize(30, 30))
        self.send_button.setStyleSheet("background-color: transparent")
        self.send_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.send_button.clicked.connect(self.send)
        self.send_button.setVisible(False)

        self.chat_info_frame = QtWidgets.QFrame(self.chat_frame)
        self.chat_info_frame.setStyleSheet(f"background-color: 'white';"
                                           f"border: 1px solid;"
                                           f"border-color: none none none {colors['gray']};")

        self.current_chat_img = QtWidgets.QLabel(self.chat_info_frame)
        self.current_chat_img.setPixmap(QtGui.QPixmap('images/close_button.png').scaled(50, 50))
        self.current_chat_img.setStyleSheet("background-color: transparent;"
                                            "border: none;")
        self.current_chat_img.setGeometry(5, 5, 50, 50)

        self.current_chat_name_label = QtWidgets.QLabel("None", self.chat_info_frame)
        self.current_chat_name_label.setGeometry(70, 0, 600, 30)
        self.current_chat_name_label.setFont(get_font(18, False, "Lato Black"))
        self.current_chat_name_label.setStyleSheet(f"color: {colors['black']};"
                                                   f"border: none;")
        self.current_chat_name_label.setContentsMargins(0, 5, 0, 0)

        self.online_label = QtWidgets.QLabel("", self.chat_info_frame)
        self.online_label.setGeometry(70, 30, 600, 30)
        self.online_label.setFont(get_font(16, False, "Lato"))
        self.online_label.setStyleSheet(f"color: {colors['black']};"
                                        f"border: none;")
        self.online_label.setContentsMargins(0, 0, 50, 5)

        self.messages_by_room = {}

        self.rooms = {r: Room(r) for r in self.client.execute({'command': 'get_rooms'})}

        for room in self.rooms.keys():
            self.messages_by_room[room] = MessageList(self.chat_frame)
            self.messages_by_room[room].hide()

        self.rooms_list = QtWidgets.QListWidget(self.contacts_frame)
        self.rooms_list.currentItemChanged.connect(self.enter_room)
        self.rooms_list.setStyleSheet(list_style)

        for room in self.rooms.values():
            item = QtWidgets.QListWidgetItem(self.rooms_list)
            item.setSizeHint(room.sizeHint())
            self.rooms_list.addItem(item)
            self.rooms_list.setItemWidget(item, room)

        self.searchbar = Entry(self, font=18, rect=(5, 12, self.contacts_frame.width(), 35), text="Search room")
        self.searchbar.setClearButtonEnabled(True)
        self.searchbar.textChanged.connect(self.search)
        self.searchbar.setStyleSheet(entry_style())

        self.no_results_label = QtWidgets.QLabel("No rooms found", self.contacts_frame)
        self.no_results_label.setFont(get_font(18, False, "Lato Light"))
        self.no_results_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.no_results_label.setContentsMargins(5, 5, 5, 5)
        self.no_results_label.move(self.contacts_frame.width() // 2 - self.no_results_label.width() // 2,
                                   self.rooms_list.pos().y() + 10)
        self.no_results_label.resize(self.contacts_frame.width(), 30)
        self.no_results_label.hide()

        self.welcome_label = QtWidgets.QLabel("Select a room to start messaging", self.chat_frame)
        self.welcome_label.setFont(get_font(20, False, "Lato"))
        self.welcome_label.setContentsMargins(10, 5, 10, 5)
        self.welcome_label.adjustSize()
        self.welcome_label.setStyleSheet(f"color: white;"
                                         f"background-color: rgba(0, 0, 0, 50);"
                                         f"border-radius: {self.welcome_label.height() // 2}px")
        self.welcome_label.move(self.chat_frame.width() // 2 - self.welcome_label.width() // 2,
                                self.chat_frame.height() // 2 - self.welcome_label.height() // 2)

        self.chat_info_frame.hide()
        self.typing_area.hide()
        self.setFocus()
        self.show()
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)

        for c in self.client.execute({'command': "get_online"}):
            self.client_entered(c)

        self.messages_thread = Listener(self.client, self)
        self.messages_thread.msg_signal.connect(self.add_message)
        self.messages_thread.entered_signal.connect(self.client_entered)
        self.messages_thread.start()

    def add_message(self, data):
        self.messages_by_room[self.current_room].add_message(text=data['message'],
                                                             author_name=data['name'], author_username=data['username'],
                                                             side=('left' if data['username'] == USERNAME else 'right'))

    def enter_room(self, current: QtWidgets.QListWidgetItem, former):
        room_widget = self.rooms_list.itemWidget(current)

        if former is not None:
            self.rooms_list.itemWidget(former).name_label.setStyleSheet(f"color: {colors['black']};"
                                                                        f"background-color: transparent;")
            self.rooms_list.itemWidget(former).online_label.setStyleSheet(f"color: {colors['black']};"
                                                                          f"background-color: transparent;")
            self.messages_by_room[self.rooms_list.itemWidget(former).name].hide()
            self.messages_by_room[self.rooms_list.itemWidget(former).name].add_message(text="You left the room",
                                                                                       side="center")
        else:
            self.chat_info_frame.show()
            self.typing_area.show()
            self.welcome_label.hide()

        self.messages_by_room[room_widget.name].show()

        self.rooms_list.itemWidget(current).name_label.setStyleSheet(f"color: white;"
                                                                     f"background-color: transparent;")
        self.rooms_list.itemWidget(current).online_label.setStyleSheet(f"color: white;"
                                                                       f"background-color: transparent;")

        self.current_chat_name_label.setText(room_widget.name)
        self.current_chat_img.setPixmap(QtGui.QPixmap(f"images/{room_widget.name}").scaled(50, 50))

        self.client.send({'command': "enter_room", 'parameters': {'room': room_widget.name}})

    def client_entered(self, data):
        room_name, username = data['room'], data['username']

        for room in self.rooms.values():
            if username in room.online:
                room.online.remove(username)
                room.update_online()
                if room.name == self.current_room:
                    self.messages_by_room[self.current_room].add_message(
                            text=f"{username if username != USERNAME else 'You'} left the room",
                            side="center")

        if room_name in self.rooms:
            self.rooms[room_name].online.append(username)
            self.rooms[room_name].update_online()

        if self.current_room != "None":
            self.online_label.setText(self.rooms[self.current_room].online_label.text())
            self.online_label.adjustSize()

        if room_name != "None":
            if room_name == self.current_room:
                self.messages_by_room[self.current_room].add_message(
                        text=f"{username if username != USERNAME else 'You'} joined the room",
                        side="center")

    def search(self, text):
        for i in range(self.rooms_list.count()):
            item = self.rooms_list.item(i)
            item.setHidden(text.lower() not in self.rooms_list.itemWidget(item).name.lower())

        for i in range(self.rooms_list.count()):
            item = self.rooms_list.item(i)
            if not item.isHidden():
                self.no_results_label.hide()
                break
        else:
            self.no_results_label.show()

    def send(self):
        msg = self.entry.toPlainText().strip()
        self.entry.clear()

        self.client.send({'command': "send_message", 'parameters': {'message': msg}})

    @property
    def current_room(self):
        return self.current_chat_name_label.text()

    def set_geometries(self):
        self.contacts_frame.setGeometry(0, 0, int(self.width() * 0.25), self.height())
        self.searchbar.setFixedWidth(self.contacts_frame.width() - 10)
        self.rooms_list.setGeometry(0, 60, self.contacts_frame.width(), self.contacts_frame.height() - 60)
        self.chat_frame.setGeometry(self.contacts_frame.width(), 0, self.width() - self.contacts_frame.width(),
                                    self.height())
        self.welcome_label.move(self.chat_frame.width() // 2 - self.welcome_label.width() // 2,
                                self.chat_frame.height() // 2 - self.welcome_label.height() // 2)
        height = int(min((self.entry.document().size().height()) + 10, 120))
        self.typing_area.setGeometry(0, self.height() - height, self.chat_frame.width(), height)
        self.entry.setGeometry(0, 0, self.chat_frame.width(), height)
        self.send_button.move(self.typing_area.width() - self.send_button.width(),
                              self.typing_area.height() - self.send_button.height())
        self.chat_info_frame.setGeometry(0, 0, self.chat_frame.width(), 60)
        for messages in self.messages_by_room.values():
            messages.setGeometry(0, self.chat_info_frame.height(), self.chat_frame.width(),
                                 self.chat_frame.height() - self.chat_info_frame.height() - self.entry.height())
        self.no_results_label.resize(self.contacts_frame.width(), 30)
        self.no_results_label.move(self.contacts_frame.width() // 2 - self.no_results_label.width() // 2,
                                   self.rooms_list.pos().y())

    def typing(self):
        if re.match(r"\s", self.entry.toPlainText()):
            self.entry.setText(self.current_msg)
            return
        self.current_msg = self.entry.toPlainText()

        self.set_geometries()

        self.send_button.setVisible(len(self.entry.toPlainText()) > 0)
        self.send_button.setEnabled(self.send_button.isVisible())

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        super(Chat, self).resizeEvent(a0)

        self.set_geometries()


class Listener(QtCore.QThread):
    msg_signal = QtCore.pyqtSignal(dict)
    entered_signal = QtCore.pyqtSignal(dict)

    def __init__(self, client, parent=None):
        super(Listener, self).__init__(parent)

        self.client = client

    def run(self):
        while True:
            try:
                r = self.client.receive()
            except:
                break

            if r["type"] == "message":
                self.msg_signal.emit(r["data"])
            if r["type"] == "client_entered":
                self.entered_signal.emit(r["data"])
