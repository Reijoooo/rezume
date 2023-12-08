import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize

def error_function_L(params):
    a, b = params
    predicted_y_L = a * x_array + b
    error = np.sum((y_L_with_noise - predicted_y_L)**2)
    return error

def error_function_K(params):
    a, b, c = params
    predicted_y_K = a * x_array ** 2 + b * x_array + c
    error = np.sum((y_K_with_noise - predicted_y_K)**2)
    return error

if __name__ == '__main__':

    # Зададим значения варианта
    a: int = 6 # Придуманный коэффициент
    b: int = 7 # Придуманный коэффициент
    c: int = 5 # Придуманный коэффициент
    k = 0.01 # Шаг значений x
    n = 500 # Количество измерений x

    x = [] # Создаём пустой массив для значений x


    # Заполним массив x элементами i*k
    for i in range(n):
        x.append(i * k)

    # -----------------------------------------------------------------------------------------------
    # Построим функцию линейного графика
    y_L = [a * x + b for x in x]

    # Выведем график
    plt.plot(x, y_L, label='y(x) = {}x + {}'.format(a, b))
    plt.title('График линейной функции y(x) = {}x + {}'.format(a, b))
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Построим функцию квадратичного графика
    y_K = [a * x ** 2 + b * x + c for x in x]

    plt.plot(x, y_K, label='y(x) = {}x^2 + {}x + {}'.format(a, b, c))
    plt.title('График квадратичной функции y(x) = {}x^2 + {}x + {}'.format(a, b, c))
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.grid(True)
    plt.show()

    # -----------------------------------------------------------------------------------------------
    # Добавим шум к линейному графику
    y_L_N = [a * x_val  + b for x_val  in x]

    noise_L = np.random.normal(0, 1, len(x))  # Генерируем случайный шум
    y_L_with_noise = y_L_N + noise_L  # Добавляем шум к значениям y

    plt.plot(x, y_L_with_noise, label='y(x) = {}x + {} с шумом'.format(a, b))
    # Накладываем график без шума
    plt.plot(x, y_L, label='y(x) = {}x + {} без шума'.format(a, b), color='orange')
    plt.title('График линейной функции y(x) = {}x + {} с шумом'.format(a, b))
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Добавим шум к квадратичному графику
    y_K_N = [a * x_val ** 2 + b * x_val + c for x_val in x]

    noise_K = np.random.normal(0, 1, len(x))  # Генерируем случайный шум
    y_K_with_noise = y_K_N + noise_K  # Добавляем шум к значениям y

    plt.plot(x, y_K_with_noise, label='y(x) = {}x^2 + {}x + {} с шумом'.format(a, b, c))
    # Накладываем график без шума
    plt.plot(x, y_K, label='y(x) = {}x^2 + {}x + {} без шума'.format(a, b, c), color='orange')
    plt.title('График квадратичной функции y(x) = {}x^2 + {}x + {} с шумом'.format(a, b, c))
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.grid(True)
    plt.show()

    # -----------------------------------------------------------------------------------------------
    # Нахождение коэффициентов зашумленной линейной функции методом МНК
    # Создание матрицы X
    X_L = np.column_stack([x, np.ones(len(x))])

    # Решение системы линейных уравнений X * β = y
    beta = np.linalg.lstsq(X_L, y_L_with_noise, rcond=None)[0]

    # Получение коэффициентов a, b и c
    a_r_l, b_r_l = beta

    print()
    print('Коэффициенты линейной квадратичной функции')
    print(f"a = {a_r_l}, b = {b_r_l}")

    # График линейной функции по восстановленным коэффициентам
    reconstructed_y_L = [a_r_l * x + b_r_l for x in x]

    plt.figure(figsize=(8, 6))
    plt.plot(x, y_L_with_noise, label='Зашумленные данные', color='blue')
    plt.plot(x, reconstructed_y_L, label='Восстановленная линейная функция', color='red')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.title('График восстановленной функции из зашумленных данных')
    plt.grid(True)
    plt.show()

    # Нахождение коэффициентов зашумленной квадратичной функции методом МНК
    # Преобразуем массив
    x_array = np.array(x)

    # Создание матрицы X
    x_squared = x_array ** 2
    X_K = np.column_stack([x_squared, x_array, np.ones(len(x))])

    # Решение системы линейных уравнений X * β = y
    beta = np.linalg.lstsq(X_K, y_K_with_noise, rcond=None)[0]

    # Получение коэффициентов a, b и c
    a_r_k, b_r_k, c_r_k = beta

    print()
    print('Коэффициенты зашумленной квадратичной функции')
    print(f"a = {a}, b = {b}, c = {c}")

    # График квадратичной функции по восстановленным коэффициентам
    reconstructed_y_K = [a_r_k * x ** 2 + b_r_k * x + c_r_k for x in x]

    plt.figure(figsize=(8, 6))
    plt.plot(x, y_K_with_noise, label='Зашумленные данные', color='blue')
    plt.plot(x, reconstructed_y_K, label='Восстановленная квадратичная функция', color='red')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.title('График восстановленной функции из зашумленных данных')
    plt.grid(True)
    plt.show()

    # -----------------------------------------------------------------------------------------------
    # МНК в дифференциальной форме для линейной функции
    # Начальное приближение для параметров a и b
    initial_guess = [1.0, 1.0]

    # Минимизация функции ошибки
    result_L = minimize(error_function_L, initial_guess, method='L-BFGS-B')

    # Получение оптимальных параметров
    optimal_params = result_L.x
    a_optimal_L, b_optimal_L = optimal_params

    print()
    print(f"Оптимальные параметры для линейной: a = {a_optimal_L}, b = {b_optimal_L}")

    y_optimal_L = [a_optimal_L * x + b_optimal_L for x in x]

    plt.plot(x, y_L_with_noise, label='Зашумленные данные', color='blue')
    plt.plot(x, y_optimal_L, label='Квадратичная функция', color='purple')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.title('График линейной функции по оптимальным данным')
    plt.grid(True)
    plt.show()

    # МНК в дифференциальной форме для квадратичной функции
    # Начальное приближение для параметров a и b
    initial_guess = [1.0, 1.0, 1.0]

    # Минимизация функции ошибки
    result_K = minimize(error_function_K, initial_guess, method='L-BFGS-B')

    # Получение оптимальных параметров
    optimal_params = result_K.x
    a_optimal_K, b_optimal_K, c_optimal_K = optimal_params

    print()
    print(f"Оптимальные параметры для квадратичной: a = {a_optimal_K}, b = {b_optimal_K}, c = {c_optimal_K}")

    y_optimal_K = [a_optimal_K * x ** 2 + a_optimal_K * x + c_optimal_K for x in x]

    plt.plot(x, y_K_with_noise, label='Зашумленные данные', color='blue')
    plt.plot(x, y_optimal_K, label='Линейная функция', color='purple')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.title('График квадратичной функции по оптимальным данным')
    plt.grid(True)
    plt.show()

    # -----------------------------------------------------------------------------------------------
    # График линейной функции МНК матричной и дифференциальной
    plt.plot(x, reconstructed_y_L, label='МНК матричная', color='red')
    plt.plot(x, y_optimal_L, label='МНК дифференциальная', color='blue')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.title('Графики линейной функции')
    plt.grid(True)
    plt.show()

    # График квадратичной функции МНК матричной и дифференциальной
    plt.plot(x, reconstructed_y_K, label='МНК матричная', color='red')
    plt.plot(x, y_optimal_K, label='МНК дифференциальная', color='blue')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.title('Графики квадратичной функции')
    plt.grid(True)
    plt.show()

    # -----------------------------------------------------------------------------------------------