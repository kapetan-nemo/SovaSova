from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from game import Game


class MyTable(QTableWidget):
    def __init__(self, *args):
        QTableWidget.__init__(self, *args)

    def event(self, event):
        if (event.type() == QEvent.KeyPress) and (event.key() == Qt.Key_Tab):
            self.emit(pyqtSignal("tabPressed"))
            self.emi
            return True

        return QTableWidget.event(self, event)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # Структура окно -> центральный виджет -> один из переключаемых виджетов -> локальный layout ->
        # локальные sublayout и widgets
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.initial_widget = ToursQuestWindow(self)
        self.initial_widget.button.clicked.connect(self.create_game)
        self.central_widget.addWidget(self.initial_widget)

        # self.setStyleSheet("QPushButton {font: 11pt Spectral} QLabel {font: 11pt Spectral} "
        #                    "QSpinBox {font: 11pt Spectral} QLineEdit {font: 11pt Spectral}")
        self.setStyleSheet("QWidget {font: 11pt Spectral}")
        # self.setStyleSheet("QWidget {font: 11pt Sans Serif}")

        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        # self.setPalette(p)

    def create_game(self):
        game_name = self.initial_widget.game_name_text.text()
        tours_qnt = self.initial_widget.tours_spin.value()
        quest_qnt = self.initial_widget.quest_spin.value()

        results_widget = ResultsTable(self, game_name, tours_qnt, quest_qnt)
        self.central_widget.addWidget(results_widget)
        self.central_widget.setCurrentWidget(results_widget)
        self.resize(1000, 200)
        print("Name: %s, tours: %d, questions: %d\n" % (game_name, tours_qnt, quest_qnt))


class ToursQuestWindow(QWidget):
    def __init__(self, parent=None):
        super(ToursQuestWindow, self).__init__(parent)

        layout = QGridLayout()

        self.parent().setWindowTitle("Sova x qqha")

        self.game_name_label = QLabel("Название игры: ")
        self.game_name_text = QLineEdit("")

        self.tours_label = QLabel("Количество туров: ")
        self.tours_spin = QSpinBox(self)
        self.tours_spin.setValue(3)

        self.quest_label = QLabel("Количество вопросов: ")
        self.quest_spin = QSpinBox(self)
        self.quest_spin.setValue(12)

        self.button = QPushButton('Создать игру')
        # self.button.setFlat(True)

        sublayout1 = QGridLayout()
        sublayout1.addWidget(self.game_name_label, 0, 0)
        sublayout1.addWidget(self.game_name_text, 0, 1)

        sublayout2 = QGridLayout()
        sublayout2.addWidget(self.tours_spin, 0, 1)
        sublayout2.addWidget(self.tours_label, 0, 0)
        sublayout2.addWidget(self.quest_label, 1, 0)
        sublayout2.addWidget(self.quest_spin, 1, 1)

        layout.addLayout(sublayout1, 0, 0)
        layout.addLayout(sublayout2, 1, 0)
        layout.addWidget(self.button, 2, 0)

        self.setLayout(layout)
        print(layout.sizeHint())


class ResultsTable(QWidget):
    def __init__(self, parent=None, game_name="", tours=3, questions=12):
        super(ResultsTable, self).__init__(parent)

        self.game_name = game_name
        self.tours = tours
        self.quest = questions
        self.game = Game(name=self.game_name, tours=self.tours, questions=self.quest)

        self.parent().setWindowTitle("%s - Sova x qqha" % self.game_name)

        layout = QGridLayout()

        # создание таблицы с результатами
        self.table = MyTable(self)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setColumnCount(1 + (questions + 2) * tours + 1 + 1 + 1)  # Устанавливаем  колонки
        # название команды | вопросы + сумма взятых + сумма спорных | сумма за игру | сумма спорных | рейтинг |
        self.table.setRowCount(0)
        self.table.clicked.connect(self.change_results)
        self.table.setLineWidth(10)
        self.table.setContentsMargins(10, 10, 10, 10)
        header = list()
        header.append("Команда")
        for k in range(0, tours):
            [header.append(("%d" % (x + k * questions))) for x in range(1, questions + 1)]
            header.append(("За тур №%d" % (k + 1)))
            header.append(("Спорные за тур №%d" % (k + 1)))
        header.append("Сумма за игру")
        header.append("Спорные за игру")
        header.append("Рейтинг")

        self.table.setHorizontalHeaderLabels(header)
        self.table.selectedIndexes()
        # Виджеты для добавления новой команды
        # TODO: добавление команды в последнюю пустую строку таблицы по вводу названия и нажатия Enter
        # TODO: как-то зафиксировать первый столбец при прокрутке
        # TODO: добавить про спорные вопросы
        self.new_team_label = QLabel("Название новой команды: ")
        self.new_team_text = QLineEdit()
        self.new_team_text.returnPressed.connect(self.add_team)

        self.new_team_button = QPushButton("Добавить")
        # self.new_team_button.setFlat(True)
        self.new_team_button.clicked.connect(self.add_team)

        new_team_layout = QGridLayout()
        new_team_layout.addWidget(self.new_team_label, 0, 0)
        new_team_layout.addWidget(self.new_team_text, 0, 1)
        new_team_layout.addWidget(self.new_team_button, 0, 2)

        # добавление на layout
        layout.addWidget(self.table, 0, 0)
        layout.addLayout(new_team_layout, 1, 0)
        self.setLayout(layout)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.resizeColumnsToContents()

    def add_team(self):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        # вставить имя команды
        item = QTableWidgetItem(self.new_team_text.text())
        item.setTextAlignment(Qt.AlignCenter)

        self.table.setItem(row_position, 0, item)

        # по дефолту за вопросы минус, результаты тура 0
        for k in range(0, self.tours):
            for x in range(0, self.quest):
                self.table.setItem(row_position, 1 + x + k * self.quest + k + k, QTableWidgetItem("-"))
                self.table.item(row_position, 1 + x + k * self.quest + k + k).setTextAlignment(Qt.AlignCenter)
                self.table.item(row_position, 1 + x + k * self.quest + k + k).setFlags(Qt.ItemIsEnabled)

            # взятые за тур
            self.table.setItem(row_position, (k + 1) * (self.quest + 2) - 1, QTableWidgetItem("0"))
            self.table.item(row_position, (k + 1) * (self.quest + 2) - 1).setTextAlignment(Qt.AlignCenter)
            self.table.item(row_position, (k + 1) * (self.quest + 2) - 1).setFlags(Qt.ItemIsEnabled)

            # спорные за тур
            self.table.setItem(row_position, (k + 1) * (self.quest + 2), QTableWidgetItem("0"))
            self.table.item(row_position, (k + 1) * (self.quest + 2)).setTextAlignment(Qt.AlignCenter)
            self.table.item(row_position, (k + 1) * (self.quest + 2)).setFlags(Qt.ItemIsEnabled)

        # результат за игру ноль
        self.table.setItem(row_position, self.tours * (self.quest + 2) + 1, QTableWidgetItem("0"))
        self.table.item(row_position, self.tours * (self.quest + 2) + 1).setTextAlignment(Qt.AlignCenter)

        # спорные ноль
        self.table.setItem(row_position, self.tours * (self.quest + 2) + 2, QTableWidgetItem("0"))
        self.table.item(row_position, self.tours * (self.quest + 2) + 2).setTextAlignment(Qt.AlignCenter)

        # рейтинг ноль
        self.table.setItem(row_position, self.tours * (self.quest + 2) + 3, QTableWidgetItem("0"))
        self.table.item(row_position, self.tours * (self.quest + 2) + 3).setTextAlignment(Qt.AlignCenter)

        self.game.add_team(self.new_team_text.text())

        self.new_team_text.clear()
        self.table.resizeColumnsToContents()

        # заполнить результаты
        self.show_results()

    def change_results(self, signal):
        current_row = signal.row()
        current_col = signal.column() - 1

        num_tour = divmod(current_col, self.quest + 2)[0]
        num_ques = current_col - num_tour * 2

        rng = []
        [rng.extend(list(range(0 + (self.quest + 2) * x, self.quest + (self.quest + 2) * x))) for x in range(0, 3)]

        if current_col in rng:
            local_quest = divmod(num_ques, self.quest)[1]

            print("col #%d, team #%d, tour #%d, ques #%d, local ques #%d" % (current_col, current_row + 1, num_tour + 1,
                                                                             num_ques + 1, local_quest + 1))
            symbol = self.game.set_result(team_index=current_row, tour_index=num_tour, question_index=local_quest)

            self.table.setItem(current_row, current_col + 1, QTableWidgetItem(symbol))
            self.table.item(current_row, current_col + 1).setTextAlignment(Qt.AlignCenter)
            self.table.item(current_row, current_col + 1).setFlags(Qt.ItemIsEnabled)
            print(symbol)

            self.show_results()

        self.table.resizeColumnsToContents()

    def show_results(self):
        print(self.table.rowCount())
        for team_index in range(0, self.table.rowCount()):
            for tour_index in range(0, self.tours):
                # заполнение результата за тур
                tour_result = str(int(self.game.get_tour_result(team_index, tour_index)))
                self.table.setItem(team_index, (tour_index + 1) * (self.quest + 2) - 1, QTableWidgetItem(tour_result))
                self.table.item(team_index, (tour_index + 1) * (self.quest + 2) - 1).setTextAlignment(Qt.AlignCenter)
                self.table.item(team_index, (tour_index + 1) * (self.quest + 2) - 1).setFlags(Qt.ItemIsEnabled)

                tour_disput = str(int(self.game.get_tour_disput(team_index, tour_index)))
                self.table.setItem(team_index, (tour_index + 1) * (self.quest + 2), QTableWidgetItem(tour_disput))
                self.table.item(team_index, (tour_index + 1) * (self.quest + 2)).setTextAlignment(Qt.AlignCenter)
                self.table.item(team_index, (tour_index + 1) * (self.quest + 2)).setFlags(Qt.ItemIsEnabled)

            total_result = str(int(self.game.get_total_result(team_index)))
            self.table.setItem(team_index, self.tours * (self.quest + 2) + 1, QTableWidgetItem(total_result))
            self.table.item(team_index, self.tours * (self.quest + 2) + 1).setTextAlignment(Qt.AlignCenter)
            self.table.item(team_index, self.tours * (self.quest + 2) + 1).setFlags(Qt.ItemIsEnabled)

            total_disput = str(int(self.game.get_total_disput(team_index)))
            self.table.setItem(team_index, self.tours * (self.quest + 2) + 2, QTableWidgetItem(total_disput))
            self.table.item(team_index, self.tours * (self.quest + 2) + 2).setTextAlignment(Qt.AlignCenter)
            self.table.item(team_index, self.tours * (self.quest + 2) + 2).setFlags(Qt.ItemIsEnabled)

            rating = str(int(self.game.get_rating(team_index)))
            self.table.setItem(team_index, self.tours * (self.quest + 2) + 3, QTableWidgetItem(rating))
            self.table.item(team_index, self.tours * (self.quest + 2) + 3).setTextAlignment(Qt.AlignCenter)
            self.table.item(team_index, self.tours * (self.quest + 2) + 3).setFlags(Qt.ItemIsEnabled)

        print("\n")


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
