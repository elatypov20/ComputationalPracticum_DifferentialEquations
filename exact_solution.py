from abc import ABC, abstractmethod

class ExactSolution(ABC):
    def __init__(self, x0, y0):
        pass

    @abstractmethod
    def get_solution(self, x):
        pass

    @abstractmethod
    def build_solution(self, X, N):
        pass

    @abstractmethod
    def build_range(self, x0, X, N):
        pass

    @abstractmethod
    def get_discontinuities(self):
        pass


class MySolution(ExactSolution):
    def __init__(self, x0, y0, *kwargs):
        super().__init__(x0, y0)

        x0 = float(x0)
        y0 = float(y0)

        self.x0 = x0
        self.y0 = y0

        sign_x0 = 1 if x0 >=  0 else -1

        self.C = ((sign_x0 * abs(x0)**(1/3)) * (2 - x0 * y0)) / (x0 * y0 - 1)

    """
    generates exact solution (function) for given initial values
    """
    def get_solution(self, x):
        sign_x = 1 if x >=  0 else -1
        return 1 / x + 1 / (x + (sign_x * abs(x) ** (2 / 3)) * self.C)

    def get_discontinuities(self):
        return {0, -(self.C ** 3)}

    """
    generates points for given input
    """
    def build_solution(self, X, N, *kwargs):
        step = (X - self.x0) / N

        x_points = []
        y_points = []


        x = self.x0
        while x <= X:
            x_points += [x]
            y_points += [self.get_solution(x)]
            x += step

        return x_points, y_points

    def build_range(self, x0, X, N, **kwargs):
        cur_x0 = self.x0
        self.x0 = x0

        x_points, y_points = self.build_solution(X, N)

        self.x0 = cur_x0

        return x_points, y_points


# tests
if __name__ == '__main__':
    exact_solution = MySolution(1, 2)

    # should be equal to 2
    print(exact_solution.get_solution(1))

    # should be equal to 1
    print(exact_solution.get_solution(2))

    # should be equal to 0.2
    print(exact_solution.get_solution(10))

    print(list(zip(*exact_solution.build_solution(5, 10))))



