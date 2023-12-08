import math

import numpy as np
from scipy.optimize import curve_fit, minimize
import matplotlib.pyplot as plt
import sympy as sp


def func(x, a0, a1):
    res = a0 * np.exp(x * a1)
    return res

def sum_xi(x):
    return np.sum(x)

def sum_xi_pow2(x):
    squared_x = np.power(x, 2)
    return np.sum(squared_x)

def YS_xi(y_n_ln, x):
    res = y_n_ln * x
    return np.sum(res)
def YS(y_n_ln):
    return np.sum(y_n_ln)

if __name__ == '__main__':
    # Зададим значения варианта
    a0 = 9.0
    a1 = 4.0
    k = 0.01  # Шаг значений x
    n = 500.0  # Количество измерений x

    # Заполняем массив x элементами
    x = np.arange(1, n * k + 1, k)

    # -----------------------------------------------------------------------------------------------
    # Построим функцию
    y = func(x, a0, a1)

    # Выведем график
    plt.plot(x, y, label=f'$f(x) = {a0} \cdot e^{{x \cdot {a1}}}$')
    plt.title('График функции $f(x) = {a0} \cdot e^{{x \cdot {a1}}}$')
    plt.title(f'График функции $f(x) = {a0} \cdot e^{{x \cdot {a1}}}$\nс коэффициентами: $a_0 = {a0}$, $a_1 = {a1}$')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.grid(True)
    plt.show()

    # -----------------------------------------------------------------------------------------------
    # Добавим шум
    # noise_1 = np.random.normal(0, 22, len(x))  # Генерируем случайный шум
    y_n = y + np.random.normal(1, 22) - 22/2 # Добавляем шум к значениям y
    # print(y_n)
    # Накладываем с шумом
    plt.plot(x, y_n, label=f'$f(x) = {a0} \cdot e^{{x \cdot {a1}}}$', color='orange')
    plt.title('График функции $f(x) = {a0} \cdot e^{{x \cdot {a1}}}$ с шумом')
    plt.xlabel('x')
    plt.ylabel('y с шумом')
    plt.legend(['$f(x) = {a0} \cdot e^{{x \cdot {a1}}}$ с шумом', '$f(x) = {a0} \cdot e^{{x \cdot {a1}}}$ без шума'],
               loc='upper left')
    plt.grid(True)
    plt.show()
    # -----------------------------------------------------------------------------------------------

    #Логарифмируем зашумленную функцию
    y_n_ln = np.log(y_n)
    print('lg(y_n)=', y_n_ln)

    #новый коэф.
    b0 = math.log(a0)
    b1 = a1
    print('b0=', b0)

    A_matrix = np.array([
        [n,              sum_xi(x)],
        [sum_xi(x),     sum_xi_pow2(x) ]
    ])

    print('A_matrix = ',A_matrix)

    C_matrix = np.array([
        [YS(y_n_ln)],
        [YS_xi(y_n_ln, x)]
    ])

    print('C_matrix = ',C_matrix)
    A_1_matrix = np.linalg.inv(A_matrix)

    X_matrix = np.dot(A_1_matrix,C_matrix)

    print('X_matrix = ', X_matrix)

    a0_final = np.exp(X_matrix[0][0])
    print('a0_final = ',a0_final)
    a1_final = X_matrix[1][0]
    print('a1_final = ',a1_final)
