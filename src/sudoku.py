

class Square(object):
    def __init__(self, init_number, idx):
        self.idx = idx
        if init_number == 0:
            self.possible_numbers = list(range(1, 10))
        else:
            self.possible_numbers = [init_number]

    def remove(self, number):
        if not self.solved:
            try:
                self.possible_numbers.remove(number)
            except ValueError:
                return False

        return True

    @property
    def value(self):
        return self.possible_numbers[0]

    def __str__(self):
        if self.solved:
            return str(self.value)
        else:
            return " "

    @property
    def solved(self):
        return len(self.possible_numbers) == 1



class Board(object):
    def __init__(self, board_list):
        "docstring"
        assert len(board_list) == 81
        self.board_list = [Square(s, i) for i, s in enumerate(board_list)]

    @property
    def solved(self):
        return all(s.solved for s in self.board_list)

    def solve(self):
        something_happended = True
        while not self.solved and something_happended:
            something_happended = False
            for i, s in enumerate(self.board_list):
                if not s.solved:
                    continue
                associates = self.find_associated(i)
                for associate in associates:
                    if associate.remove(s.value):
                        something_happended = True
                        
    def solve2(self):
        solved_squares = {s for s in self.board_list if s.solved}
        while solved_squares:
            s = solved_squares.pop()
            associates = self.find_associated(s.idx)
            for associate in associates:
                if associate.remove(s.value):
                    if associate.solved:
                        solved_squares.add(associate)

    def find_associated(self, idx):
        row = idx // 9
        col = idx % 9
        quad = 3 * (row // 3) + col // 3
        associates = set()
        for i in range(9):
            a_idx = row * 9 + i
            if a_idx != idx and not self.board_list[a_idx].solved:
                associates.add(self.board_list[a_idx])

        for i in range(9):
            a_idx = i * 9 + col
            if a_idx != idx and not self.board_list[a_idx].solved:
                associates.add(self.board_list[a_idx])

        startpos = 27*int(quad/3) + 3*int(quad % 3)
        for i in range(3):
            for j in range(3):
                a_idx = startpos + i*9 + j
                if a_idx != idx and not self.board_list[a_idx].solved:
                    associates.add(self.board_list[a_idx])
        return associates
            
    def print_board(self):
        for i in range(9):
            tmp_str = ""
            for j in range(9):
                idx = i * 9 + j
                tmp_str += str(self.board_list[idx])
            print(tmp_str)

    

c = Board([4,0,0,0,0,3,0,0,0,3,2,9,0,0,7,0,4,5,0,1,0,0,2,9,0,0,3,0,0,0,7,0,0,3,9,6,1,0,7,0,0,0,5,0,4,9,5,3,0,0,6,0,0,0,8,0,0,2,6,0,0,7,0,6,9,0,5,0,0,8,3,2,0,0,0,3,0,0,0,0,1])

c.print_board()
c.solve()
#c.solve2()
print("====================")
c.print_board()
