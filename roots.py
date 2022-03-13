from math import *
from sympy.parsing.sympy_parser import parse_expr
import sympy
import traceback
import steffensen
import scipy

# sympy.init_printing(use_unicode=True)

ITER_EXCESS = 201
BAD_ROOT = 202
FUNC_UNDEF = 301

BY_DEF = 0
FROM_LIB = 1


class State:
    function = ""
    first_der = second_der = third_der = ""
    epsilon = 1e-5
    iter_max = 100
    method = FROM_LIB

    def update_derivs(self):
        x_symbol = sympy.symbols('x')
        self.first_der = str(sympy.diff(parse_expr(self.function), x_symbol))
        self.second_der = str(sympy.diff(parse_expr(self.function), x_symbol, 2))
        self.third_der = str(sympy.diff(parse_expr(self.function), x_symbol, 3))
        # print(self.third_der)
        # print("DERIVS: ", self.first_der, self.second_der)

    def set_method(self, method):
        self.method = method

    def set_exp(self, expression):
        self.function = expression

    def set_iter_max(self, iter_max):
        self.iter_max = iter_max

    def set_epsilon(self, epsilon):
        self.epsilon = epsilon


state = State()

    
def func_eval(x):
    value = None
    try:
        value = eval(state.function.replace('x', '('+str(x)+')'))
    except:
        pass
    return value


def get_1st_der(x):
    if state.method == BY_DEF:
        tmp_value = func_eval(x + state.epsilon)
        if tmp_value is None:
            return None
        tmp = tmp_value - func_eval(x)
        return tmp / state.epsilon
    elif state.method == FROM_LIB:
        value = None
        try:
            value = eval(state.first_der.replace('x', '('+str(x)+')'))
        except:
            pass
        return value


def get_2nd_der(x):
    if state.method == BY_DEF:
        der_1 = get_1st_der(x)
        der_2 = get_1st_der(x + state.epsilon)
        if der_1 is None or der_2 is None:
            return None
        return (der_2 - der_1) / state.epsilon
    elif state.method == FROM_LIB:
        value = None
        try:
            value = eval(state.second_der.replace('x', '('+str(x)+')'))
        except:
            pass
        return value


def get_3rd_der(x):
    if state.method == BY_DEF:
        der_1 = get_1st_der(x)
        der_2 = get_1st_der(x + state.epsilon)
        if der_1 is None or der_2 is None:
            return None
        return (der_2 - der_1) / state.epsilon
    elif state.method == FROM_LIB:
        value = None
        try:
            value = eval("-4*x*(2*x**2*cos(x**2) + 3*sin(x**2))".replace('x', '('+str(x)+')'))
            # value = eval(state.third_der.replace('x', str(x)))
        except Exception as err:
            print("FALSE X:", x)
            traceback.print_exc()
        return value


def get_extremums(start, step, end):
    return find_roots(start, step, end, function=get_1st_der)


def get_inflection_points(start, step, end):
    return find_roots(start, step, end, function=get_2nd_der)


def find_roots(start, step, end, function=func_eval):
    i = 0
    local_start = start
    local_end = start + step
    while local_start < end:
        root, cnt, code = find_root(start + (i + .5) * step, function)
        if isnan(root):
            code = FUNC_UNDEF
        value = func_eval(root)
        point = (root, value)

        if value is None:
            code = FUNC_UNDEF
        else:
            if local_start <= root < local_end:
                pass
            else:
                point = (float("nan"), float("nan"))
                code = BAD_ROOT

        yield point, local_start, local_end, cnt, code,

        i += 1
        local_start = start + i * step
        local_end = min(start + (i + 1) * step, end)


def new_x(x, function=func_eval):
    if function == func_eval:
        return x - func_eval(x) / get_1st_der(x)
    if function == get_1st_der:
        return x - get_1st_der(x) / get_2nd_der(x)
    if function == get_2nd_der:
        return x - get_2nd_der(x) / get_3rd_der(x)

# def new_x(x, function=func_eval):
#     func_value = function(x)
#     if func_value is None:
#         return None
#     new_value = function(x + func_value)
#     if new_value is None:
#         return None
#     divisor = new_value - func_value
#     if divisor == 0:
#         divisor = state.epsilon
#     res = x - func_value * func_value / divisor
#     return res


def find_root(start, function=func_eval):
    return steffensen.steffensen(function, start, state.epsilon)
    # x = start
    # x_last = None
    # cnt = 0
    # while x_last is None or abs(x_last - x) > state.epsilon:
    #     cnt += 1
    #     x_last = x
    #     x = new_x(x, function)
    #     if x is None:
    #         return float("nan"), cnt, FUNC_UNDEF
    #     # print("\t\tCalcs:", cnt, x)
    #     if cnt > state.iter_max:
    #         return x, cnt, ITER_EXCESS
    # if abs(function(x)) <= state.epsilon:
    #     # print("Inter:", x, func(x))
    #     return x, cnt, 0
    # return x, cnt, BAD_ROOT


# state.update_derivs()
# state.method = FROM_LIB
# print(get_2nd_der(2))
#
# x_symbol, y_symbol = sympy.symbols('x y')
# expr = sympy.cos(x_symbol)
# print(expr.diff(x_symbol))
# sympy.diff(sympy.cos(x_symbol), x_symbol)