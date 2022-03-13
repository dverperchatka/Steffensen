from tkinter import *
import matplotlib
import matplotlib.pyplot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from numpy import *
import traceback

import roots
import roots as roots_funcs


widgets = dict()
roots_widgets = dict()

disabled_digit_color = "Silver"
normal_digit_color = "White"
normal_button_color = "Gainsboro"
background_color = "Silver"
display_color = "LightGrey"


class State:
    orig_width = cur_width = 1200
    orig_height = cur_height = 800
    disp_height = int(orig_height/6)
    disp_diff = 0
    min_multi = 1.
    max_font_height = 20
    min_font_height = 1
    orig_disp_height = orig_disp_width = 0
    window = None
    plot_x = linspace(0, 20 * pi, 100)
    plot_y = plot_x  # sin(plot_x + 3)

    roots = dict()
    extremums = dict()
    inflection_points = dict()

    start = end = step = 0


state = State()


def on_resize(size):
    """Updates all widget and font sizes"""
    state.cur_width = size.width
    state.cur_height = size.height
    state.min_multi = min(size.width/state.orig_width, size.height/state.orig_height)
    state.min_multi = pow(state.min_multi, 1 / 3)
    # canvas.blit()


def create_input_field(row_, column_, text_var, columnspan_=1, row_weight=4):
    window.grid_rowconfigure(row_, weight=row_weight)
    window.grid_columnconfigure(column_, weight=2)
    field = Entry(
        window, textvariable=text_var, bg=display_color, width=0, justify="right", font=("Courier", int(20))
    )
    widgets[(row_, column_)] = field
    field.grid(row=row_, column=column_, columnspan=columnspan_, sticky="news")


def create_label(row_, column_, text_, columnspan_=1, column_weight=1):
    window.grid_rowconfigure(row_, weight=1)
    window.grid_columnconfigure(column_, weight=column_weight)
    label = Label(
        window, text=text_, bg=display_color, justify="right", font=("Courier", int(14))
    )
    widgets[(row_, column_)] = label
    label.grid(row=row_, column=column_, columnspan=columnspan_, sticky="news")


roots_headers = []
canvas = None
sub_plot = None
plot_line = None
matplotlib.pyplot.ion()


def matplot_canvas():
    global canvas, sub_plot, plot_line
    fig = matplotlib.figure.Figure(figsize=(1, 1), dpi=100)
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.get_tk_widget().bind("<Button-1>", func=lambda event: update_function_field(event))
    sub_plot = fig.add_subplot(111)
    plot_line, = sub_plot.plot(state.plot_x, state.plot_y, 'b-')
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)
    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
    canvas.draw()


def build_graph():
    sub_plot.clear()
    sub_plot.plot(state.plot_x, state.plot_y, 'b-')

    sub_plot.plot(state.roots.keys(), state.roots.values(), marker='o', linestyle='', color='red')
    sub_plot.plot(state.extremums.keys(), state.extremums.values(), marker='o', linestyle='', color='navy')
    sub_plot.plot(state.inflection_points.keys(), state.inflection_points.values(), marker='o', linestyle='', color='green')
    sub_plot.legend([roots_funcs.state.function, 'roots', 'extremums', 'inflection points'], loc=2)

    sub_plot.grid(True)
    canvas.draw()


def input_process(x):
    """Process input from keyboard"""
    char_ = x
    if type(char_) != str:
        char_ = x.char
    char_ = char_.upper()
    # print(char)
    # if char_ in 'AaФф':


def update_function_field(x):
    expression = text_variables[0].get()
    roots_funcs.state.function = expression
    roots_funcs.state.set_exp(expression)
    state.start = float(text_variables[1].get())
    state.end = float(text_variables[2].get())
    state.step = float(text_variables[3].get())
    roots_funcs.state.set_iter_max(int(text_variables[4].get()))
    roots_funcs.state.set_epsilon(float(text_variables[5].get()))
    try:
        if roots_funcs.state.method == roots_funcs.FROM_LIB:
            roots_funcs.state.update_derivs()
        state.plot_x = linspace(state.start, state.end, int((state.end - state.start) / state.step))
        state.plot_y = eval(expression.replace('x', 'state.plot_x'))

        flush_headers()

        state.roots = {
            process_header(data, i, "root"): data[0][1] for i, data in
            enumerate(roots_funcs.find_roots(state.start, state.step, state.end))
        }
        state.extremums = {
            process_header(data, 1, "extremum"): data[0][1] for data in
            roots_funcs.get_extremums(state.start, state.step, state.end)
        }
        state.inflection_points = {
            process_header(data, -1, "pivot"): data[0][1] for data in
            roots_funcs.get_inflection_points(state.start, state.step, state.end)
        }

        build_graph()
    except Exception as err:
        traceback.print_exc()


def create_roots_label(parent, row_, column_, text_, columnspan_=1, column_weight=1):
    parent.grid_rowconfigure(row_, weight=1)
    parent.grid_columnconfigure(column_, weight=column_weight)
    label = Label(
        parent, text=text_, bg=display_color, width=10, justify="right", font=("Courier", int(14))
    )
    widgets[(row_, column_)] = label
    label.pack(side=LEFT, fill=BOTH, expand=True)


def create_roots_header(parent, text_vars):
    header = Frame(parent)
    roots_headers.append(header)
    header.pack(side=TOP, fill=BOTH)
    create_roots_label(header, 0, 0, text_vars[0])
    create_roots_label(header, 0, 1, text_vars[1])
    create_roots_label(header, 0, 2, text_vars[2])
    create_roots_label(header, 0, 3, text_vars[3])
    create_roots_label(header, 0, 4, text_vars[4])
    create_roots_label(header, 0, 5, text_vars[5])


def flush_headers():
    for widget in roots_headers[1:]:
        widget.pack_forget()
    if len(roots_headers) == 0:
        text_vars = ["№ корня", "[xi; xi+1]", "x’", "f(x’)", "Количество\nитераций", "Код\nошибки"]
        create_roots_header(roots_frame, text_vars)


def process_header(data, counter, type):
    if data[4] != roots_funcs.BAD_ROOT:
        root_x_str = '{:.4g}'.format(data[0][0])
        root_y_str = '{:.1f}'.format(data[0][1])
        start_str = '{:.4g}'.format(data[1])
        stop_str = '{:.4g}'.format(data[2])
        iters = '{:d}'.format(data[3])
        code = '{:d}'.format(data[4])
        text_vars = [type, '[' + start_str + '; ' + stop_str + ']', root_x_str, root_y_str, iters, code]

        create_roots_header(roots_frame, text_vars)

    return data[0][0]


if __name__ == '__main__':
    window = Tk()
    state.window = window
    window.config(background=background_color)
    window.title("Kekmos")
    window.geometry("1600x600")
    window.bind_class("Tk", sequence="<Configure>", func=on_resize)

    text_variables = [StringVar() for i in range(6)]
    text_variables[0].set("sin(x)")
    text_variables[1].set("-1")
    text_variables[2].set("1.5")
    text_variables[3].set(".2")
    text_variables[4].set("100")
    text_variables[5].set("1e-5")

    graph_frame = Frame(window)
    window.grid_rowconfigure(0, weight=10)
    window.grid_columnconfigure(0, weight=1)
    graph_frame.grid(row=0, column=0, columnspan=6, sticky="news")

    matplot_canvas()

    create_input_field(1, 0, text_variables[0], columnspan_=6)

    create_label(2, 0, "Start")
    create_label(2, 1, "End")
    create_label(2, 2, "Step")
    create_label(2, 3, "Iter")
    create_label(2, 4, "Eps")
    create_label(2, 5, "Method")

    for i in range(5):
        create_input_field(3, i, text_variables[i + 1], row_weight=1)

    roots_container = Frame(window)
    roots_canvas = Canvas(roots_container)
    scrollbar = Scrollbar(roots_container, orient="vertical", command=roots_canvas.yview)
    roots_frame = Frame(roots_canvas)
    roots_frame.bind("<Configure>", lambda event: roots_canvas.configure(scrollregion=roots_canvas.bbox("all")))
    canvas_frame = roots_canvas.create_window((0, 0), window=roots_frame, anchor="nw")
    roots_canvas.bind('<Configure>', lambda event: roots_canvas.itemconfig(canvas_frame, width=event.width))
    roots_canvas.configure(yscrollcommand=scrollbar.set)

    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(6, weight=10)
    roots_container.grid(row=0, column=6, rowspan=4, sticky="news")
    roots_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    method_var = IntVar()
    method_var.set(1)
    method_frame = Frame(window)

    definition_method = Radiobutton(master=method_frame, text='By definition', variable=method_var, value=0,
                                    command=lambda: roots_funcs.state.set_method(roots_funcs.BY_DEF), bg="lightgray")
    library_method = Radiobutton(master=method_frame, text='From senpai', variable=method_var, value=1,
                                 command=lambda: roots_funcs.state.set_method(roots_funcs.FROM_LIB), bg="lightgray")

    window.grid_rowconfigure(3, weight=1)
    window.grid_columnconfigure(5, weight=1)
    method_frame.grid(row=3, column=5, sticky="news")
    definition_method.pack(side="top", fill="both", expand=True)
    library_method.pack(side="top", fill="both", expand=True)  #

    window.grid_rowconfigure(0, weight=30)
    update_function_field(None)
    window.mainloop()
