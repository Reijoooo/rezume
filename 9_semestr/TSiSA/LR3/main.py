import numpy as np
from scipy.optimize import curve_fit, minimize
import matplotlib.pyplot as plt

def func(x, a0, a1, a2):
    res = a2 * x**2 + a1 * x + a0
    return res

# Функция ошибки (сумма квадратов разностей)
def error_function(coeffs, x, y):
    a0, a1, a2 = coeffs
    return np.sum((y - func(x, a0, a1, a2))**2)

if __name__ == '__main__':
    # Зададим значения варианта
    a0 = 6.0
    a1 = 3.0
    a2 = 4.0
    k = 0.01  # Шаг значений x
    n = 500.0  # Количество измерений x

    # Заполняем массив x элементами
    x = np.arange(1, n * k + 1, k)

    # -----------------------------------------------------------------------------------------------
    # Построим функцию
    y = func(x, a0, a1, a2)

    # Выведем график
    plt.plot(x, y, label=f'$f(x) = {a2} \cdot x^2 + {a1} \cdot x + {a0}$', color='blue')
    plt.title(f'График функции $f(x) = {a2} \cdot x^2 + {a1} \cdot x + {a0}$')
    plt.title(f'График функции $f(x) = {a2} \cdot x^2 + {a1} \cdot x + {a0}$\nс коэффициентами: a0 = {a0}, a1 = {a1}, a2 = {a2}')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.grid(True)
    plt.show()

    # -----------------------------------------------------------------------------------------------
    # Добавим шум
    n = np.random.normal(0, 1, y.shape) # Добавляем шум к значениям y
    y_n = y + n
    # Накладываем с шумом
    plt.plot(x, y_n, label=f'$f(x) = {a2} \cdot x^2 + {a1} \cdot x + {a0}$', color='orange')
    plt.title(f'График функции $f(x) = {a2} \cdot x^2 + {a1} \cdot x + {a0}$ с шумом')
    plt.plot(x, y, label=f'$f(x) = {a2} \cdot x^2 + {a1} \cdot x + {a0}$', color='blue')
    plt.title(f'График функции $f(x) = {a2} \cdot x^2 + {a1} \cdot x + {a0}$ без шума')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.grid(True)
    plt.show()
    # -----------------------------------------------------------------------------------------------
    # МНК Матричная форма
    # Создание матрицы плана (X)
    X = np.column_stack((x ** 2, x, np.ones_like(x)))

    # Вычисление коэффициентов
    coefficients = np.linalg.inv(X.T @ X) @ X.T @ y_n
    a2_est, a1_est, a0_est = coefficients

    print("Матричная форма")
    print("a0 восстановленный: ", a0_est)
    print("a1 восстановленный: ", a1_est)
    print("a2 восстановленный: ", a2_est)
    print()

    # Построение аппроксимирующей функции
    y_est = func(x, a0_est, a1_est, a2_est)

    # Отображение графиков
    plt.plot(x, y_n, 'o', label='Зашумленные данные')
    plt.plot(x, y, label='Исходная функция')
    plt.plot(x, y_est, label='Аппроксимация методом наименьших квадратов')
    plt.legend()
    plt.show()
    # -----------------------------------------------------------------------------------------------
    # МНК дифференциальная форма
    # Первоначальные оценки коэффициентов
    initial_guess = [1, 1, 1]

    # Оптимизация
    result = minimize(error_function, initial_guess, args=(x, y_n))

    # Полученные коэффициенты
    a0_est, a1_est, a2_est = result.x

    print("Дифференциальная форма")
    print("a0 восстановленный: ", a0_est)
    print("a1 восстановленный: ", a1_est)
    print("a2 восстановленный: ", a2_est)
    print()

    # Построение графика
    plt.plot(x, y_n, 'o', label='Зашумленные данные')
    plt.plot(x, func(x, a0_est, a1_est, a2_est), label='Аппроксимация')
    plt.legend()
    plt.show()
    # -----------------------------------------------------------------------------------------------
    # Графики линейных функций, полученных МНК в дифференциальной и матричной форме

    plt.plot(x, y_est, label='матричная')
    plt.plot(x, func(x, a0_est, a1_est, a2_est), label='дифференциальная')
    plt.legend()
    plt.show()
    # -----------------------------------------------------------------------------------------------
    # Построение гистограммы шума
    plt.hist(n, bins=50, color='red', edgecolor='black', alpha=0.7)
    plt.title('Гистограмма исходного шума')
    plt.xlabel('Значение шума')
    plt.ylabel('Частота')
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()
    # -----------------------------------------------------------------------------------------------
    # Вычисление среднего значения
    mean = np.mean(y_n)

    # Вычисление среднеквадратичного отклонения
    std_deviation = np.std(y_n)

    # Вычисление коэффициента вариации
    coefficient_of_variation = (std_deviation / mean) * 100  # в процентах

    # Вывод результатов
    print("Значения до распределения")
    print(f"Среднее значение: {mean}")
    print(f"Среднеквадратичное отклонение: {std_deviation}")
    print(f"Коэффициент вариации: {coefficient_of_variation}%")
    print()

    # -----------------------------------------------------------------------------------------------
    uniform_noise = np.random.uniform(0, 1, y.shape)

    # Построение гистограммы для равномерно распределенного шума
    plt.hist(uniform_noise, bins=50, color='red', edgecolor='black', alpha=0.7, density=True)
    plt.ylabel('Частота')
    plt.xlabel('Значение шума')
    plt.title('Гистограмма равномерно распределенного шума')
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()
    # -----------------------------------------------------------------------------------------------
    # Вычисление среднего значения
    mean = np.mean(uniform_noise)

    # Вычисление среднеквадратичного отклонения
    std_deviation = np.std(uniform_noise)

    # Вычисление коэффициента вариации
    coefficient_of_variation = (std_deviation / mean) * 100  # в процентах

    # Вывод результатов
    print("Значения после распределения")
    print(f"Среднее значение: {mean}")
    print(f"Среднеквадратичное отклонение: {std_deviation}")
    print(f"Коэффициент вариации: {coefficient_of_variation}%")
    print()

    # Коэффициент вариации и среднеквадратичное отклонение близки к 0, что подтверждает равномерное распределение значений шума.
    # -----------------------------------------------------------------------------------------------
    y_noisy_uniform = y + uniform_noise

    # Аппроксимация зашумленной функции методом наименьших квадратов
    # Используйте curve_fit или другой метод оптимизации, если необходимо
    popt_uniform, _ = curve_fit(func, x, y_noisy_uniform)

    # Построение графика
    plt.figure(figsize=(10, 5))
    plt.plot(x, y, label='Исходная функция', color='blue')
    plt.plot(x, func(x, *popt_uniform), label='Аппроксимация с равномерным шумом', color='red')
    plt.title('Сравнение исходной функции и функции с равномерным шумом')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.grid(True)
    plt.show()

    # -----------------------------------------------------------------------------------------------

    # Вычисление коэффициентов
    coefficients = np.linalg.inv(X.T @ X) @ X.T @ y_noisy_uniform
    a2_est_uniform, a1_est_uniform, a0_est_uniform = coefficients

    print("Матричная форма uniform")
    print("a0 восстановленный: ", a0_est_uniform)
    print("a1 восстановленный: ", a1_est_uniform)
    print("a2 восстановленный: ", a2_est_uniform)
    print()

    # Построение аппроксимирующей функции
    y_est_uniform = func(x, a0_est_uniform, a1_est_uniform, a2_est_uniform)

    # Отображение графиков
    plt.plot(x, y, label='Исходная функция', color='blue')
    plt.plot(x, y_est_uniform, label='Аппроксимация', color='red')
    plt.title("Матричная форма")
    plt.legend()
    plt.show()
    # -----------------------------------------------------------------------------------------------
    # МНК дифференциальная форма
    # Первоначальные оценки коэффициентов
    initial_guess = [1, 1, 1]

    # Оптимизация
    result = minimize(error_function, initial_guess, args=(x, y_noisy_uniform))

    # Полученные коэффициенты
    a0_est_uniform, a1_est_uniform, a2_est_uniform = result.x

    print("Дифференциальная форма uniform")
    print("a0 восстановленный: ", a0_est_uniform)
    print("a1 восстановленный: ", a1_est_uniform)
    print("a2 восстановленный: ", a2_est_uniform)
    print()

    # Построение графика
    plt.plot(x, y, label='Исходная функция', color='blue')
    plt.plot(x, func(x, a0_est, a1_est, a2_est), label='Аппроксимация', color='red')
    plt.title("Дифференциальная форма")
    plt.legend()
    plt.show()
    # -----------------------------------------------------------------------------------------------
    plt.plot(x, y_est_uniform, label='Аппроксимация матричная', color='blue')
    plt.plot(x, func(x, a0_est, a1_est, a2_est), label='Аппроксимация дифференциальная', color='red')
    plt.legend()
    plt.show()