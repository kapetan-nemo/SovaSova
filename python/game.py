import datetime
import numpy as np


class Game(object):
    def __init__(self, name='', tours=3, questions=12):
        self._name = name
        self._date = datetime.date.today()

        self.teams = list()
        self._tours = tours
        self._questions = questions

        self._results = np.zeros((0, self._tours, self._questions), dtype='int')
        self._success_results = np.zeros((0, self._tours), dtype='int')
        self._disputable_results = np.zeros((0, self._tours), dtype='int')

        self._question_rating = np.ones((self._tours, self._questions), dtype='int')
        self._team_rating = np.zeros((0, self._tours, self._questions), dtype='int')
        pass

    def add_team(self, team_name="One more team"):
        self.teams.append(team_name)

        self._results = np.concatenate((self._results, np.zeros((1, self._tours, self._questions))))
        self._success_results = np.concatenate((self._success_results, np.zeros((1, self._tours))))
        self._disputable_results = np.concatenate((self._disputable_results, np.zeros((1, self._tours))))

        self._question_rating += 1
        self._team_rating = np.concatenate((self._team_rating, np.zeros((1, self._tours, self._questions))))

        self.calc_rating()

    def rem_team(self, team_index):
        self.teams.pop(team_index)
        self._results = np.delete(self._results, team_index, 0)

        self.calc_rating()

    def set_result(self, team_index, tour_index, question_index):
        '''
        *  1 - правильный;
        *  0 - неправильный;
        * -1 - спорный.
        Граф перехода - (0, 1, -1).
        В случае перехода  0 ->  1 соответствующий элемент массива _success_results    изменяется на +1
        В случае перехода  1 -> -1 соответствующий элемент массива _success_results    изменяется на -1, соответствующий элемент массива _disputable_results изменяется на +1
        В случае перехода -1 ->  0 соответствующий элемент массива _disputable_results изменяется на -1
        '''
        if self._results[team_index][tour_index][question_index] == 0:
            self._results[team_index][tour_index][question_index] = 1
            self._success_results[team_index][tour_index] += 1

            self._question_rating[tour_index][question_index] -= 1

        elif self._results[team_index][tour_index][question_index] == 1:
            self._results[team_index][tour_index][question_index] = -1
            self._success_results[team_index][tour_index] -= 1
            self._disputable_results[team_index][tour_index] += 1

            self._question_rating[tour_index][question_index] += 1

        else:
            self._results[team_index][tour_index][question_index] = 0
            self._disputable_results[team_index][tour_index] -= 1

        self.calc_rating()

    def calc_rating(self):
        self._team_rating = self._question_rating * np.array(self._results == 1, dtype='int')

    def get_tour_result(self, team_index, tour_index):
        return self._success_results[team_index][tour_index]

    def get_total_result(self, team_index):
        return np.sum(self._success_results[team_index])

    def get_rating(self, team_index):
        return np.sum(self._team_rating[team_index])
