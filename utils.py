from PyQt6.QtCore import QTime, QTimer, QDate


def get_delta_time(todo):
    try:
        return QTime.currentTime().msecsTo(
            QTime.fromString(str(todo[2]).split()[1], "HH:mm:ss")
        )
    except IndexError:
        return -1


def date_time_formatter_fromdb(todo_data):
    date = str(todo_data[2]).split()[0]
    time = str(todo_data[2]).split()[1]
    return [QDate.fromString(date, "yyyy-MM-dd"), QTime.fromString(time, "HH:mm:ss")]
