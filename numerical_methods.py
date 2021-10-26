from abc import ABC, abstractmethod


def dy_over_dx(x, y):
    return - ((y * y) / 3) - 2 / (3 * x * x)


class NumericalMethod(ABC):
    def __init__(self):
        pass

    def build_solution(self, x0, y0, X, N, **kwargs):
        step = (X - x0) / N

        x_points = [x0]
        y_points = [y0]

        x0 += step

        i = 1
        while x0 <= X:
            x_points += [x0]
            y_points += [y_points[i - 1] + self.recurrent_formula(x_points[i - 1], y_points[i - 1], step)]
            x0 += step
            i += 1

        return x_points, y_points

    @abstractmethod
    def recurrent_formula(self, prev_x, prev_y, step):
        pass

    def get_lte(self, x0, y0, X, N, exact_solution, **kwargs):
        x_points, approximate = self.build_solution(x0, y0, X, N)
        _, exact = exact_solution.build_solution(X, N)

        errors = []
        for appr, ex in zip(approximate, exact):
            errors += [abs(ex - appr)]

        return x_points, errors

    def get_gte(self, x0, y0, X, n, N, exact_solution, **kwargs):
        max_errors = []

        for steps in range(n, N + 1):
            max_errors += [max(self.get_lte(x0, y0, X, steps, exact_solution)[1])]

        return list(range(n, N + 1)), max_errors



class EulerMethod(NumericalMethod):
    def __init__(self):
        super().__init__()

    def recurrent_formula(self, prev_x, prev_y, step):
        return step * dy_over_dx(prev_x, prev_y)



class ImprovedEulerMethod(NumericalMethod):
    def __init__(self):
        super().__init__()

    def recurrent_formula(self, prev_x, prev_y, step):
        return step * dy_over_dx(prev_x + step / 2, prev_y + (step / 2) * dy_over_dx(prev_x, prev_y))

class RungeKuttaMethod(NumericalMethod):
    def __init__(self):
        super().__init__()

    def recurrent_formula(self, prev_x, prev_y, step):
        half_step = step /  2

        k1 = dy_over_dx(prev_x, prev_y)
        k2 = dy_over_dx(prev_x + half_step, prev_y + half_step * k1)
        k3 = dy_over_dx(prev_x + half_step, prev_y + half_step * k2)
        k4 = dy_over_dx(prev_x + step, prev_y + step * k3)

        return (step / 6) * (k1 + 2 * k2 + 2 * k3 + k4)


# tests
if __name__ == '__main__':
    from exact_solution import MySolution

    solution = MySolution(1, 2)

    merge = lambda a: list(zip(*a))

    euler = EulerMethod()
    print(merge(euler.build_solution(1, 2, 5, 10)))
    print()
    print(merge(euler.get_lte(1, 2, 5, 10, solution)))
    print()
    print()

    improved_euler = ImprovedEulerMethod()
    print(merge(improved_euler.build_solution(1, 2, 5, 10)))
    print()
    print(merge(improved_euler.get_lte(1, 2, 5, 10, solution)))
    print()
    print()

    runge_kutta = RungeKuttaMethod()
    print(merge(runge_kutta.build_solution(1, 2, 5, 10)))
    print()
    print(merge(runge_kutta.get_lte(1, 2, 5, 10, solution)))
    print()
    print()
