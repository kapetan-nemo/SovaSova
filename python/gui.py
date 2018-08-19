from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from game import Game


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # Структура окно -> центральный виджет -> один из переключаемых виджетов -> локальный layout ->
        # локальные sublayout и widgets
        self.setWindowTitle("SovaSova")
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.initial_widget = ToursQuestWindow(self)
        self.initial_widget.button.clicked.connect(self.create_game)
        self.central_widget.addWidget(self.initial_widget)

    def create_game(self):
        game_name = self.initial_widget.game_name_text.text()
        tours_qnt = self.initial_widget.tours_spin.value()
        quest_qnt = self.initial_widget.quest_spin.value()

        results_widget = ResultsTable(self, game_name, tours_qnt, quest_qnt)
        self.central_widget.addWidget(results_widget)
        self.central_widget.setCurrentWidget(results_widget)

        print("Name: %s, tours: %d, questions: %d\n" % (game_name, tours_qnt, quest_qnt))


class ToursQuestWindow(QWidget):
    def __init__(self, parent=None):
        super(ToursQuestWindow, self).__init__(parent)

        layout = QGridLayout()

        self.game_name_label = QLabel("Название игры: ")
        self.game_name_text = QLineEdit("")

        self.tours_label = QLabel("Количество туров: ")
        self.tours_spin = QSpinBox(self)
        self.tours_spin.setValue(2)

        self.quest_label = QLabel("Количество вопросов: ")
        self.quest_spin = QSpinBox(self)
        self.quest_spin.setValue(2)

        self.button = QPushButton('Создать игру')

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

        layout = QGridLayout()

        # создание таблицы с результатами
        self.table = QTableWidget(self)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setColumnCount(1 + (questions + 1) * tours + 1 + 1)  # Устанавливаем  колонки
        self.table.setRowCount(0)
        self.table.doubleClicked.connect(self.change_results)

        header = list()
        header.append("Команда")
        for k in range(0, tours):
            [header.append(("%d" % (x + k * questions))) for x in range(1, questions + 1)]
            header.append(("За тур №%d" % (k + 1)))
        header.append("Сумма за игру")
        header.append("Рейтинг")

        self.table.setHorizontalHeaderLabels(header)

        # Виджеты для добавления новой команды
        self.new_team_label = QLabel("Название новой команды: ")
        self.new_team_text = QLineEdit()

        self.new_team_button = QPushButton("Добавить")
        self.new_team_button.clicked.connect(self.add_team)

        new_team_layout = QGridLayout()
        new_team_layout.addWidget(self.new_team_label, 0, 0)
        new_team_layout.addWidget(self.new_team_text, 0, 1)
        new_team_layout.addWidget(self.new_team_button, 0, 2)

        # добавление на layout
        layout.addWidget(self.table, 0, 0)
        layout.addLayout(new_team_layout, 1, 0)
        self.setLayout(layout)

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
                self.table.setItem(row_position, 1 + x + k * self.quest + k, QTableWidgetItem("-"))
                self.table.item(row_position, 1 + x + k * self.quest + k).setTextAlignment(Qt.AlignCenter)
                self.table.item(row_position, 1 + x + k * self.quest + k).setFlags(Qt.ItemIsEnabled)

            self.table.setItem(row_position, (k + 1) * (self.quest + 1), QTableWidgetItem("0"))
            self.table.item(row_position, (k + 1) * (self.quest + 1)).setTextAlignment(Qt.AlignCenter)
            self.table.item(row_position, (k + 1) * (self.quest + 1)).setFlags(Qt.ItemIsEnabled)

        # результат за игру ноль
        self.table.setItem(row_position, self.tours * (self.quest + 1) + 1, QTableWidgetItem("0"))
        self.table.item(row_position, self.tours * (self.quest + 1) + 1).setTextAlignment(Qt.AlignCenter)
        # рейтинг ноль
        self.table.setItem(row_position, self.tours * (self.quest + 1) + 2, QTableWidgetItem("0"))
        self.table.item(row_position, self.tours * (self.quest + 1) + 2).setTextAlignment(Qt.AlignCenter)
        self.game.add_team(self.new_team_text.text())

        self.new_team_text.clear()
        self.table.resizeColumnsToContents()

        # заполнить результаты
        self.show_results()

    def change_results(self, signal):
        current_row = signal.row()
        current_col = signal.column() - 1

        num_tour = divmod(current_col, self.quest + 1)[0]
        num_ques = current_col - num_tour

        if (current_col >= 0) & (current_col < (self.quest + 1) * self.tours) & \
                (divmod(current_col + 1, self.quest + 1)[1] != 0):
            local_quest = divmod(num_ques, self.quest)[1]

            if self.table.item(current_row, current_col + 1).text() == "-":
                print("minus to plus")
                self.table.setItem(current_row, current_col + 1, QTableWidgetItem("+"))
                self.table.item(current_row, current_col + 1).setTextAlignment(Qt.AlignCenter)
                self.table.item(current_row, current_col + 1).setFlags(Qt.ItemIsEnabled)
            elif self.table.item(current_row, current_col + 1).text() == "+":
                print("plus to question")
                self.table.setItem(current_row, current_col + 1, QTableWidgetItem("?"))
                self.table.item(current_row, current_col + 1).setTextAlignment(Qt.AlignCenter)
                self.table.item(current_row, current_col + 1).setFlags(Qt.ItemIsEnabled)
            else:
                print("question to minus")
                self.table.setItem(current_row, current_col + 1, QTableWidgetItem("-"))
                self.table.item(current_row, current_col + 1).setTextAlignment(Qt.AlignCenter)
                self.table.item(current_row, current_col + 1).setFlags(Qt.ItemIsEnabled)

            print("col #%d, team #%d, tour #%d, ques #%d, local ques #%d" % (current_col, current_row + 1, num_tour + 1,
                                                                             num_ques + 1, local_quest + 1))
            self.game.set_result(team_index=current_row, tour_index=num_tour, question_index=local_quest)

            self.show_results()

        self.table.resizeColumnsToContents()

    def show_results(self):
        print(self.table.rowCount())
        for team_index in range(0, self.table.rowCount()):
            for tour_index in range(0, self.tours):
                # заполнение результата за тур
                tour_result = str(int(self.game.get_tour_result(team_index, tour_index)))
                self.table.setItem(team_index, (tour_index + 1) * (self.quest + 1), QTableWidgetItem(tour_result))
                self.table.item(team_index, (tour_index + 1) * (self.quest + 1)).setTextAlignment(Qt.AlignCenter)
                self.table.item(team_index, (tour_index + 1) * (self.quest + 1)).setFlags(Qt.ItemIsEnabled)

            total_result = str(int(self.game.get_total_result(team_index)))
            self.table.setItem(team_index, self.tours * (self.quest + 1) + 1, QTableWidgetItem(total_result))
            self.table.item(team_index, self.tours * (self.quest + 1) + 1).setTextAlignment(Qt.AlignCenter)
            self.table.item(team_index, self.tours * (self.quest + 1) + 1).setFlags(Qt.ItemIsEnabled)

            rating = str(int(self.game.get_rating(team_index)))
            self.table.setItem(team_index, self.tours * (self.quest + 1) + 2, QTableWidgetItem(rating))
            self.table.item(team_index, self.tours * (self.quest + 1) + 2).setTextAlignment(Qt.AlignCenter)
            self.table.item(team_index, self.tours * (self.quest + 1) + 2).setFlags(Qt.ItemIsEnabled)

        print("\n")


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
