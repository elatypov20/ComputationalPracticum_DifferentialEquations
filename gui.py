import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
import pyqtgraph as pg

from exact_solution import MySolution
from numerical_methods import EulerMethod, ImprovedEulerMethod, RungeKuttaMethod

# some constants at the beginning
DEFAULT_VALUES = {
    'x0': 1,
    'y0': 2,
    'X': 5,
    'n': 5,
    'N': 15
}

ERROR_PLOTS_OPTIONS = [
    'Euler Method',
    'Improved Euler Method',
    'Runge-Kutta Method'
]

MAIN_PLOT_OPTIONS = ERROR_PLOTS_OPTIONS + ['Analytical Solution']

pages = {
    'plot': {
        'parameters': ['x0', 'y0', 'X', 'N'],
        'options': MAIN_PLOT_OPTIONS,
        'x_axis': 'X',
        'y_axis': 'Y',
    },

    'lte': {
        'parameters': ['x0', 'y0', 'X', 'N'],
        'options': ERROR_PLOTS_OPTIONS,
        'x_axis': 'X',
        'y_axis': 'Error',
    },

    'gte': {
        'parameters': ['x0', 'y0', 'X', 'n', 'N'],
        'options': ERROR_PLOTS_OPTIONS,
        'x_axis': 'N',
        'y_axis': 'Max Error',
    },
}

euler_method = EulerMethod()
improved_euler_method = ImprovedEulerMethod()
runge_kutta_method = RungeKuttaMethod()

numerical_methods = {
    'Euler Method': {
        'color': (255, 0, 0),
        'plot': euler_method.build_solution,
        'lte': euler_method.get_lte,
        'gte': euler_method.get_gte,
    },

    'Improved Euler Method': {
        'color': (0, 255, 0),
        'plot': improved_euler_method.build_solution,
        'lte': improved_euler_method.get_lte,
        'gte': improved_euler_method.get_gte,
    },

    'Runge-Kutta Method': {
        'color': (0, 0, 255),
        'plot': runge_kutta_method.build_solution,
        'lte': runge_kutta_method.get_lte,
        'gte': runge_kutta_method.get_gte,
    },
}


def positive_int(string):
    x = int(string)
    if x <= 0:
        raise Exception('NegativeIntegerException')
    return x


verificators = {
    'x0': float,
    'y0': float,
    'X': float,
    'n': positive_int,
    'N': positive_int,
}


class MainWindow(qw.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Computation Practicum, Latypov Emil')

        self.current_page = 'plot'
        self.plotter = Plotter(self, MAIN_PLOT_OPTIONS, DEFAULT_VALUES, 'plot')
        self.configurator = Configurator(self, pages['plot']['parameters'])
        self.view_manager = ViewManager(self, pages['plot']['options'])

        self.options = MAIN_PLOT_OPTIONS
        self.parameters = DEFAULT_VALUES

    def updateGraph(self, parameters):
        for parameter in parameters:
            try:
                parameters[parameter] = verificators[parameter](parameters[parameter])
            except:
                print(f'Parameter {parameter} did not pass verification: Incorrect Input!')
                self.configurator.reconstruct(pages[self.current_page]['parameters'])
                return

        if not self.verify_parameters(parameters):
            return

        self.parameters = parameters
        self.plotter.reconstruct(self.options, self.parameters, self.current_page)

    def updateVisible(self, options):
        self.options = options
        self.plotter.reconstruct(options, self.parameters, self.current_page)

    def switch_page(self, page):
        if self.current_page == page:
            return
        self.configurator.reconstruct(pages[page]['parameters'])
        self.view_manager.reconstruct(pages[page]['options'])
        self.current_page = page
        self.plotter.reconstruct(pages[page]['options'], DEFAULT_VALUES, self.current_page)
        self.parameters = DEFAULT_VALUES

    def verify_parameters(self, params):

        if params['x0'] == 0.0:
            print('ParamError: x0 should not be equal to 0')
            return False

        if params['x0'] >= params['X']:
            print('ParamError: x0 should be grater than X!')
            return False

        if params['y0'] == 1 / params['x0']:
            print('ParamError: y0 = 1/x0 initial values are prohibited!')
            return False

        if (params['X'] - params['x0']) / params['N'] >= 1:
            print('ParamError: (X - x0) / N should be < 1!')
            return False

        if self.current_page == 'gte':
            if params['n'] >= params['N']:
                print('ParamError: N should be greater than n!')
                return False

            if (params['X'] - params['x0']) / params['n'] >= 1:
                print('ParamError: (X - x0) / n should be < 1!')
                return False

        return True



class Plotter(qw.QWidget):
    def __init__(self, master, to_draw, parameters, page):
        super().__init__(master)

        self.master = master
        self.setGeometry(0, 0, 700, 700)

        self.graph = None

        self.reconstruct(to_draw, parameters, page)

    def reconstruct(self, to_draw, parameters, page):
        self.clear()
        # print(parameters)
        self.graph = pg.PlotWidget(self)
        self.graph.setGeometry(0, 0, 700, 700)
        self.graph.setBackground('#d9fcff')
        self.graph.setTitle(page.upper(), color=(0, 0, 0), size='30pt')
        self.graph.showGrid(x=True, y=True)
        label_style = {'color': (255, 0, 0), 'font-size': '40px'}
        self.graph.setLabel('left', pages[page]['y_axis'], **label_style)
        self.graph.setLabel('bottom', pages[page]['x_axis'], **label_style)
        self.graph.setVisible(True)
        self.graph.addLegend()
        # self.graph.setAspectLocked()

        solution = MySolution(parameters['x0'], parameters['y0'])

        intervals = [solution.x0, parameters['X']]

        for disc in solution.get_discontinuities():
            if solution.x0 <= disc <= parameters['X']:
                intervals += [disc]

        intervals.sort()


        for num_method in to_draw:
            if num_method == 'Analytical Solution':
                continue

            if len(intervals) > 2:
                print('Discontinuities detected - numerical methods not applicable!')
                break

            x_points, y_points = numerical_methods[num_method][page](exact_solution=solution, **parameters)

            pen = pg.mkPen(color=numerical_methods[num_method]['color'], width=4)

            self.graph.plot(x_points, y_points, name=num_method, pen=pen)

        if page == 'plot' and 'Analytical Solution' in to_draw:
            disc_error = 0.01

            legend_printed = False

            for interval_i in range(len(intervals) - 1):
                x_points, y_points = solution.build_range(intervals[interval_i] + disc_error, intervals[interval_i + 1] - disc_error, 100)
                pen = pg.mkPen(color=(160, 109, 222), width=4, style=qc.Qt.DashLine)
                if not legend_printed:
                    self.graph.plot(x_points, y_points, name='Analytical Solution', pen=pen)
                    legend_printed = True
                else:
                    self.graph.plot(x_points, y_points, pen=pen)

    def clear(self):
        if self.graph is None:
            return
        self.graph.deleteLater()
        self.graph = None



class Configurator(qw.QWidget):
    def __init__(self, master, params, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.master = master
        self.setGeometry(700, 0, 350, 350)

        self.parameters = {}
        self.reconstruct(params)

    def reconstruct(self, params):
        self.clear()
        y_step = 40

        for i, param in enumerate(params):
            label = qw.QLabel(self)
            label.setText(param)
            label.setStyleSheet('font-size: 25px')
            label.move(10, 100 + y_step * i)

            editor = qw.QLineEdit(self)
            editor.setStyleSheet('font-size: 25px; border: 1px solid black')
            editor.resize(100, 25)
            editor.move(75, 105 + y_step * i)
            editor.setText(str(DEFAULT_VALUES[param]))
            editor.editingFinished.connect(self.updateState)

            label.setVisible(True)
            editor.setVisible(True)

            self.parameters[param] = (label, editor)

    def clear(self):
        for param in self.parameters:
            label, edit = self.parameters[param]
            label.deleteLater()
            edit.deleteLater()
        self.parameters = {}

    def updateState(self):
        states = {}
        for param in self.parameters:
            states[param] = self.parameters[param][1].text()

        self.master.updateGraph(states)



class ViewManager(qw.QWidget):
    def __init__(self, master, opt, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.master = master
        self.setGeometry(700, 350, 350, 350)

        # page switcher is static element, so it is not reconstructed each time
        self.switcher = qw.QButtonGroup(self)
        self.plot_page = qw.QPushButton(self)
        self.lte_page = qw.QPushButton(self)
        self.gte_page = qw.QPushButton(self)

        self.plot_page.resize(100, 50)
        self.lte_page.resize(100, 50)
        self.gte_page.resize(100, 50)

        self.plot_page.setText('plot')
        self.lte_page.setText('LTE')
        self.gte_page.setText('GTE')

        self.plot_page.move(25, 250)
        self.lte_page.move(125, 250)
        self.gte_page.move(225, 250)

        self.plot_page.clicked.connect(lambda: self.switch_page('Plot'))
        self.lte_page.clicked.connect(lambda: self.switch_page('LTE'))
        self.gte_page.clicked.connect(lambda: self.switch_page('GTE'))

        self.switcher.addButton(self.plot_page)
        self.switcher.addButton(self.lte_page)
        self.switcher.addButton(self.gte_page)

        # mode indicator
        self.mode_indicator = qw.QLabel(self)
        self.mode_indicator.setText('Current Mode: Plot')
        self.mode_indicator.move(0, 300)
        self.mode_indicator.resize(350, 50)
        self.mode_indicator.setStyleSheet('font-size: 20px')
        self.mode_indicator.setAlignment(qc.Qt.AlignCenter)

        # draw other elements
        self.options = {}
        self.reconstruct(opt)

    def reconstruct(self, opt):
        self.clear()

        y_step = 40
        for i, option in enumerate(opt):
            check_box = qw.QCheckBox(self)
            check_box.setText(option)
            check_box.move(10, 20 + y_step * i)
            check_box.setChecked(True)
            check_box.setVisible(True)
            check_box.setStyleSheet('font-size: 25px')
            check_box.resize(350, 50)
            check_box.clicked.connect(self.updateState)

            self.options[option] = check_box

    def clear(self):
        for option in self.options:
            self.options[option].deleteLater()

        self.options = {}

    def updateState(self):
        states = []
        for option in self.options:
            if self.options[option].isChecked():
                states += [option]

        self.master.updateVisible(states)

    def switch_page(self, page):
        self.mode_indicator.setText(f'Current Mode: {page}')
        self.master.switch_page(page.lower())
