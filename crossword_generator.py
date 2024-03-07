import random
import copy


def generate_crossword(word_list, grid_size=15, max_word=12):
    class Crossword(object):
        def __init__(self, cols, rows, empty_char='-', available_words=None):
            if available_words is None:
                available_words = []
            self.cols = cols
            self.rows = rows
            self.empty_char = empty_char
            self.available_words = available_words

            self.current_word_list = []
            self.grid = []
            self.clear_grid()

        def clear_grid(self):
            """
            initialize grid (two-dimensional list) and fill with empty character
            :return: None
            """
            self.grid = []
            for i in range(self.rows):
                grid_row = []
                for j in range(self.cols):
                    grid_row.append(self.empty_char) 
                self.grid.append(grid_row)

        def randomize_word_list(self):
            """
            resets words and sorts by length
            :return: None
            """
            temp_list = []
            for word in self.available_words:
                if isinstance(word, Word):
                    temp_list.append(Word(word.word, word.clue))
                else:
                    temp_list.append(Word(word[0], word[1]))
                    # print(Word(word[0], word[1]))
            random.shuffle(temp_list)  # randomize word list
            temp_list.sort(key=lambda i: len(i.word), reverse=True)  # sort by length
            self.available_words = temp_list

        def compute_crossword(self, spins=2):
            """
            Generate the crossword, search all the words <spins> times
            :param spins: times for searching all words
            :return: None
            """

            temp = Crossword(self.cols, self.rows, self.empty_char, self.available_words)

            temp.current_word_list = []
            temp.clear_grid()
            temp.randomize_word_list()

            for _ in range(spins):  # spins
                for word in temp.available_words:
                    if word not in temp.current_word_list:
                        # loop for every word that not in current_word_list and add into grid
                        if len(temp.current_word_list) == 0:
                            # random choose a direction for the first word
                            vertical, col, row = (
                                random.randrange(0, 2), random.randrange(0, self.cols), random.randrange(0, self.cols))
                            if temp.check_fit_score(col, row, vertical, word):
                                temp.set_word(col, row, vertical, word)

                        else:

                            coord = temp.suggest_coord(word)
                            if coord:
                                col, row, vertical = coord[0], coord[1], coord[2]
                                temp.set_word(col, row, vertical, word)

                    if len(temp.current_word_list) >= max_word:
                        # to set to max number of word appears in the grid
                        self.current_word_list = temp.current_word_list
                        self.grid = temp.grid
                        self.order_number_words()  # order the words and apply numbering system to words
                        return

            self.current_word_list = temp.current_word_list
            self.grid = temp.grid
            self.order_number_words()  # order the words and apply numbering system to words
            return

        def suggest_coord(self, word):
            """
            Find the coordinate to place the word w.r.t. current gird. The found coordinate ensures that the word letters
            match the grid letters, and that the word is within the grid, and with the highest score.
            :param word: target word
            :return: final_coord = [col, row, vertical, score] (row, col begin with 1; vertical=0, horizontal=1)
            """
            coord_list = []  # example: coord_list[0] = [col, row, vertical, score]
            for ltr_idx, word_ltr in enumerate(word.word):  # cycle through letters in word
                for row_idx, row in enumerate(self.grid):  # cycle through rows in grid
                    for col_idx, grid_ltr in enumerate(row):  # cycle through letters in rows

                        if word_ltr == grid_ltr:  # check whether letter in word matches letter in grid
                            # check the vertical placement within the grid
                            if row_idx - ltr_idx >= 0 and row_idx - ltr_idx + word.length < self.rows:
                                # starting point and end point are both within the grid
                                coord_list.append([col_idx + 1, row_idx + 1 - ltr_idx, 1, 0])

                            # check the horizontal placement with the grid
                            if col_idx - ltr_idx >= 0 and col_idx - ltr_idx + word.length < self.cols:
                                # starting point and end point are both within the grid
                                coord_list.append([col_idx + 1 - ltr_idx, row_idx + 1, 0, 0])

            # sort the coord_list according to the score
            sorted_coord_list = []
            for coord in coord_list:
                col, row, vertical = coord[0], coord[1], coord[2]
                coord[3] = self.check_fit_score(col, row, vertical, word)  # checking scores
                if coord[3] != 0:  # coordinate with 0 score is discard
                    sorted_coord_list.append(coord)
            random.shuffle(sorted_coord_list)  # randomize coord list
            sorted_coord_list.sort(key=lambda i: i[3], reverse=True)  # put the best scores first

            if sorted_coord_list:
                final_coord = sorted_coord_list[0]
            else:
                final_coord = []
            return final_coord

        def check_fit_score(self, col, row, vertical, word):
            """
            Check whether the coordinate is suitable and score the coordinate.
            Return score (0 implies not fit). 1 implies a fit, 2+ implies a cross...
            """
            if col < 1 or row < 1:
                return 0

            score = 1  # give score a standard value of 1, and override with 0 if collisions detected
            for letter_idx, letter in enumerate(word.word):

                if row <= self.rows and col <= self.cols:   # current point within the grid
                    active_cell = self.grid[row - 1][col - 1]
                else:
                    return 0

                if active_cell != self.empty_char and active_cell != letter:
                    # A collision detected
                    return 0

                if active_cell == letter:
                    score += 1

                # check surroundings to ensure do not exist an adjacent letter
                if vertical:
                    # check left and right surroundings
                    if active_cell != letter:  # not check surroundings if it is a cross point
                        if col < self.cols:    # if it is not the rightmost line, then check right cell
                            if self.grid[row - 1][col] != self.empty_char:
                                return 0
                        if col > 1:  # if it is not the leftmost line, then check left cell
                            if self.grid[row - 1][col - 2] != self.empty_char:
                                return 0

                    if letter_idx == 0 and row > 1:
                        # if it is the first letter and not the topmost cell, then check top cell
                        if self.grid[row - 2][col - 1] != self.empty_char:
                            return 0

                    if letter_idx == len(word.word) - 1 and row < self.rows:
                        # if it is the last letter and not the bottommost cell, then check bottom cell
                        if self.grid[row][col - 1] != self.empty_char:
                            return 0
                    row += 1  # increments to the next letter and position

                else:  # else horizontal placement
                    # check top and bottom surroundings
                    if active_cell != letter:  # not check surroundings if it is a cross point
                        if row < self.rows:    # if it is not the bottommost line, then check bottom cell
                            if self.grid[row][col - 1] != self.empty_char:
                                return 0
                        if row > 1:  # if it is not the topmost line, then check top cell
                            if self.grid[row - 2][col - 1] != self.empty_char:
                                return 0

                    if letter_idx == 0 and col > 1:
                        # if it is the first letter and not the leftmost cell, then check left cell
                        if self.grid[row - 1][col - 2] != self.empty_char:
                            return 0

                    if letter_idx == len(word.word) - 1 and col < self.cols:
                        # if it is the last letter and not the rightmost cell, then check right cell
                        if self.grid[row - 1][col] != self.empty_char:
                            return 0
                    col += 1  # increments to the next letter and position

            return score

        def set_word(self, col, row, vertical, word):  # also adds word to word list
            word.col = col
            word.row = row
            word.vertical = vertical
            self.current_word_list.append(word)

            for letter in word.word:
                self.set_cell(col, row, letter)
                if vertical:
                    row += 1
                else:
                    col += 1

        def set_cell(self, col, row, cell_val):
            self.grid[row - 1][col - 1] = cell_val

        def order_number_words(self):
            # order the words and apply numbering system to words
            self.current_word_list.sort(key=lambda i: (i.col + i.row))  # sort the word according to their coordinate
            count = 1
            for idx, word in enumerate(self.current_word_list):
                word.number = count
                if idx < len(self.current_word_list) - 1:
                    if (word.col != self.current_word_list[idx + 1].col or
                            word.row != self.current_word_list[idx + 1].row):
                        count += 1

        def solution_board(self):
            """
            :return: a string represents the crossword grid
            """
            out_str = ""
            for r in range(self.rows):
                for c in self.grid[r]:
                    if c == self.empty_char:
                        out_str += '  '
                    else:
                        out_str += '%s ' % c
                out_str += '\n'
            return out_str

        def word_bank(self):
            words_lst = []
            temp_word_list = copy.deepcopy(self.current_word_list)
            random.shuffle(temp_word_list)  # randomize word list
            for word in temp_word_list:
                words_lst.append(word.word)
            return words_lst

        def down_clue(self):
            vert_clue = []
            temp_word_list = copy.deepcopy(self.current_word_list)
            for word in temp_word_list:
                if word.vertical:
                    vert_clue.append([word.row - 1, word.col - 1, word.word, word.clue, word.number])
            return vert_clue

        def across_clue(self):
            horizon_clue = []
            temp_word_list = copy.deepcopy(self.current_word_list)
            for word in temp_word_list:
                if not word.vertical:
                    horizon_clue.append([word.row - 1, word.col - 1, word.word, word.clue, word.number])
            return horizon_clue
        
        def solution_list(self):
            out_list = []
            out_idx = [[] for _ in range(len(self.current_word_list))]
            words_coord = []
            temp_word_list = copy.deepcopy(self.current_word_list)
            for word in temp_word_list:
                if word.vertical:
                    words_coord.append([[word.row - 1 + i, word.col - 1] for i in range(len(word.word))])
                else:
                    words_coord.append([[word.row - 1, word.col - 1 + i] for i in range(len(word.word))])

            list_idx = 0
            for row_idx in range(self.rows):
                for col_idx in range(self.cols):
                    if self.grid[row_idx][col_idx] != self.empty_char:
                        out_list.append(self.grid[row_idx][col_idx])

                        for [word_idx, word_coord] in enumerate(words_coord):
                            for coord in word_coord:
                                if coord == [row_idx, col_idx]:
                                    out_idx[word_idx].append(list_idx)
                        list_idx += 1

            return [out_list, out_idx]

    class Word(object):
        def __init__(self, word=None, clue=None):
            self.word = word.lower()
            self.clue = clue
            self.length = len(self.word)
            # the below are set when placed on board
            self.row = None
            self.col = None
            self.vertical = None
            self.number = None

        def down_across(self):  # return down or across
            if self.vertical:
                return 'Down'
            else:
                return 'Across'

        def __repr__(self):
            return self.word

    a = Crossword(grid_size, grid_size, '', word_list)
    a.compute_crossword(5)
    # print(a.word_bank())
    # print(a.solution_board())
    # print(a.solution_list())
    return a.grid, a.across_clue(), a.down_clue(), a.solution_list(), a.word_bank()

# # example
# if __name__ == '__main__':
#     words_list = [['saffron', 'The dried, orange yellow plant used to as dye and as a cooking spice.'],
#                   ['pumpernickel', 'Dark, sour bread made from coarse ground rye.'],
#                   ['leaven', 'An agent, such as yeast, that cause batter or dough to rise..'],
#                   ['coda', 'Musical conclusion of a movement or composition.'],
#                   ['paladin', 'A heroic champion or paragon of chivalry.'],
#                   ['syncopation', 'Shifting the emphasis of a beat to the normally weak beat.'],
#                   ['albatross', 'A large bird of the ocean having a hooked beak and long, narrow wings.'],
#                   ['harp', 'Musical instrument with 46 or more open strings played by plucking.'],
#                   ['piston', 'A solid cylinder or disk that fits snugly in a larger cylinder and moves under pressure '
#                              'as in an engine.'],
#                   ['caramel', 'A smooth chery candy made from suger, butter, cream or milk with flavoring.'],
#                   ['coral', 'A rock-like deposit of organism skeletons that make up reefs.'],
#                   ['dawn', 'The time of each morning at which daylight begins.'],
#                   ['pitch', 'A resin derived from the sap of various pine trees.'],
#                   ['fjord', 'A long, narrow, deep inlet of the sea between steep slopes.'],
#                   ['lip', 'Either of two fleshy folds surrounding the mouth.'],
#                   ['lime', 'The egg-shaped citrus fruit having a green coloring and acidic juice.'],
#                   ['mist', 'A mass of fine water droplets in the air near or in contact with the ground.'],
#                   ['plague', 'A widespread affliction or calamity.'],
#                   ['yarn', 'A strand of twisted threads or a long elaborate narrative.'],
#                   ['snicker', 'A snide, slightly stifled laugh.']]

#     puzzle = generate_crossword(words_list, grid_size=15)
#     print(puzzle)







