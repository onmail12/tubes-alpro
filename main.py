import sys
import db
from winotify import Notification

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QSpacerItem,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)
from PyQt6.QtCore import QTime, QTimer, QDate, Qt
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.uic.load_ui import loadUi
from qfluentwidgets import (
    RadioButton,
    FluentIcon,
    setThemeColor,
    BodyLabel,
    Flyout,
    MessageBox,
)
from qframelesswindow import AcrylicWindow, FramelessWindow
import utils


class Window(FramelessWindow):
    def __init__(self):
        super(Window, self).__init__()
        loadUi("main.ui", self)
        self.titleBar.raise_()
        self.setWindowIcon(FluentIcon.APPLICATION.icon())
        setThemeColor("#00A4EF")

        # ui setup
        self.refresh_list()

        # set icons
        # self.btn_add_todo_item.setIcon(FluentIcon.ADD)
        self.btn_delete.setIcon(FluentIcon.DELETE)

        # SET BUTTONS
        self.PrimaryPushButton.clicked.connect(self.create_add_todo)
        self.btn_confirm_edit.clicked.connect(self.edit_todo)
        self.btn_delete.clicked.connect(self.delete_todo)
        if self.ListWidget.count() > 0:
            self.ListWidget.itemSelectionChanged.connect(self.list_on_click)

    def show_notification(self, todo):
        Notification(title=todo[1], msg=todo[3], app_id="pengingat tugas").show()
        self.refresh_list()

    def show_flyout(self, target):
        Flyout.create(
            icon=FluentIcon.CLOSE.icon(color="red"),
            title="Kesalahan",
            content="Pilih item tugas terlebih dahulu!",
            target=target,
            parent=self,
            isClosable=True,
        )

    def show_dialog(self, todo, type):
        if type == "delete":
            dialog = MessageBox(
                "Konfirmasi",
                f'Apakah anda yakin ingin menghapus tugas "{todo[1]}" ?',
                self,
            )
        elif type == "edit":
            dialog = MessageBox(
                "Konfirmasi",
                f'Apakah anda yakin ingin mengubah tugas "{todo[1]}" ?',
                self,
            )
        if dialog.exec():
            return True
        else:
            return False

    # def schedule_notification(self):
    #     for todo in db.get_all_todo():
    #         target_time = QTime.fromString(str(todo[2]).split()[1], "HH:mm:ss")
    #         # target_time = QTime.fromString("00:16:10", "HH:mm:ss")
    #         current_time = QTime.currentTime()
    #         delta_time = current_time.msecsTo(target_time)
    #         print(delta_time)

    #         self.notification_timer = QTimer()
    #         self.notification_timer.timeout.connect(self.show_notification)
    #         self.notification_timer.start(current_time.msecsTo(target_time))
    #         self.notification_timer.setSingleShot(True)

    def create_add_todo(self):
        self.add_todo = AddTodo()
        self.add_todo.show()
        self.refresh_list()

    def empty_info(self):
        self.edit_title.setText("")
        self.edit_date_picker.setDate(QDate.currentDate())
        self.edit_time_picker.setTime(QTime.currentTime())
        self.edit_note.setPlainText("")

    def refresh_list(self):
        # remove all present todo item
        current_scroll_position = self.ListWidget.verticalScrollBar().value()
        self.ListWidget.clear()
        todos = db.get_all_todo()
        # add data from db
        for todo in todos:
            list_widget_item = QtWidgets.QListWidgetItem()
            todo_widget = self.create_todo(todo[0], todo[1], todo[2], todo[3], todo[4])
            list_widget_item.setSizeHint(todo_widget.sizeHint())
            self.ListWidget.addItem(list_widget_item)
            self.ListWidget.setItemWidget(list_widget_item, todo_widget)

        # notification handler
        for todo in todos:
            if (
                todo[2]
                and utils.date_time_formatter_fromdb(todo)[0] == QDate.currentDate()
            ):
                delta_time = utils.get_delta_time(todo)
                if delta_time > 0:
                    print(f"next notification for {todo[1]} (s):", delta_time / 1000)

                    self.notification_timer = QTimer()
                    self.notification_timer.timeout.connect(
                        lambda: self.show_notification(todo)
                    )
                    self.notification_timer.start(delta_time + 500)
                    self.notification_timer.setSingleShot(True)
                    break

        self.empty_info()
        self.badge_count.setText(str(self.ListWidget.count()))

        # set scroll to prev scroll pos
        self.ListWidget.verticalScrollBar().setValue(current_scroll_position)
        self.ListWidget.clearSelection()

    def list_on_click(self):
        todo_id = self.ListWidget.itemWidget(
            self.ListWidget.item(self.ListWidget.currentRow())
        ).property("id")

        todo = db.get_one_todo(todo_id)
        print(todo)
        title = todo[1]
        self.edit_title.setText(title)

        if todo[2]:
            date, time = utils.date_time_formatter_fromdb(todo)
            self.edit_date_picker.setDate(date)
            self.edit_time_picker.setTime(time)
        else:
            self.edit_date_picker.setDate(QDate())
            self.edit_time_picker.setTime(QTime(0, 0))
        note = todo[3]
        self.edit_note.setPlainText(note)

    def delete_todo(self):
        todo = self.ListWidget.currentRow()
        if todo == -1:
            self.show_flyout(target=self.btn_delete)
        else:
            todo_id = self.ListWidget.itemWidget(self.ListWidget.item(todo)).property(
                "id"
            )
            if self.show_dialog(todo=db.get_one_todo(todo_id), type="delete"):
                db.delete_todo(todo_id)
                self.ListWidget.takeItem(todo)
                self.refresh_list()

    def edit_todo(self):
        todo = self.ListWidget.currentRow()
        if todo == -1:
            self.show_flyout(target=self.btn_confirm_edit)
        elif not self.edit_title.text() == "":
            todo_id = self.ListWidget.itemWidget(self.ListWidget.item(todo)).property(
                "id"
            )
            if self.show_dialog(todo=db.get_one_todo(todo_id), type="edit"):
                new_title = self.edit_title.text()
                date = self.edit_date_picker.getDate().toString("yyyy-MM-dd")
                time = self.edit_time_picker.getTime().toString("HH:mm:ss")
                date_time = date + " " + time
                note = self.edit_note.toPlainText()
                db.edit_todo(todo_id, new_title, date_time, note)
                self.refresh_list()
            self.edit_title.setText("")

    def complete_task(self, id):
        db.delete_todo(id)
        self.refresh_list()

    def create_todo(self, id, title, date_time=None, note=None, created_date=None):
        self.todo_item = QWidget()
        self.todo_item.setObjectName("todo_item")
        self.todo_item.setAutoFillBackground(False)
        # self.todo_item.setStyleSheet('background: "#e0e0e0"\n' "")
        self.horizontalLayout = QHBoxLayout(self.todo_item)
        self.horizontalLayout.setSpacing(16)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.radio_todo_item = RadioButton(self.todo_item)

        self.radio_todo_item.toggled.connect(lambda: self.complete_task(id))

        self.radio_todo_item.setObjectName("radio_todo_item")
        self.horizontalLayout.addWidget(self.radio_todo_item)
        self.widget_todo_item_detail = QWidget(self.todo_item)
        self.widget_todo_item_detail.setObjectName("widget_todo_item_detail")
        self.verticalLayout_7 = QVBoxLayout(self.widget_todo_item_detail)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, -1)
        self.title_todo_item = BodyLabel(title, self.widget_todo_item_detail)
        self.title_todo_item.setObjectName("title_todo_item")
        font = QFont()
        font.setPointSize(12)
        self.title_todo_item.setFont(font)

        self.verticalLayout_7.addWidget(self.title_todo_item)

        date = QDate.fromString(str(date_time).split()[0], "yyyy-MM-dd")
        self.date_todo_item = BodyLabel(
            date.toString("dddd, d MMMM"), self.widget_todo_item_detail
        )
        font1 = QFont()
        font1.setPointSize(8)
        self.date_todo_item.setFont(font1)
        self.date_todo_item.setStyleSheet("color: #696969")

        if date_time:
            self.verticalLayout_7.addWidget(self.date_todo_item)

        self.lbl_created_date.setText(f"Dibuat pada {created_date}")

        self.horizontalLayout.addWidget(self.widget_todo_item_detail)
        self.hspace_todo_item = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.horizontalLayout.addItem(self.hspace_todo_item)

        # self.icon_note = IconWidget(self.todo_item).setFixedSize(12,12)
        # self.icon_note.setIcon(FluentIcon.QUICK_NOTE)
        # self.horizontalLayout.addWidget(self.icon_note)

        self.todo_item.setProperty("id", id)

        return self.todo_item


class AddTodo(AcrylicWindow):
    def __init__(self):
        super(AddTodo, self).__init__()
        loadUi("add_todo.ui", self)
        self.main_window = window
        self.btn_confirm_add.clicked.connect(self.add_todo)

    def add_todo(self):
        self.date = self.add_date_picker.getDate().toString("yyyy-MM-dd")
        self.time = self.add_time_picker.getTime().toString("HH:mm:ss")

        self.title = self.add_title.text()
        self.date_time = self.date + " " + self.time
        if not self.title == "":
            db.add_todo(
                self.title, self.date_time, QDate.currentDate().toString("yyyy-MM-dd")
            )
            self.close()
            self.main_window.refresh_list()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Window()
    window.show()

    app.exec()
