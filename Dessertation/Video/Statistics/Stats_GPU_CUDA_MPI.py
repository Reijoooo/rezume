"""
Запускает одновременно 2 файла (пока я хуй знать как сделать график модный для сравнения скорости)

Пока что все тесты исключительно на глаз
Теоретически запускаются одновременно, но запрос идет в первую очередь на CPU обработку
Тест 1: Используя VRAM(cuda) скорость немного быстрее
Тест 2: При запуске классов(оба обрабатываются с помощью GPU) задержка меньше при использовании VRAM
"""

import subprocess
import multiprocessing

if __name__ == ('__main__'):

    script_path1 = "../GPU/ObjectDetectionClass/main.py"
    script_path2 = "../GPU/ObjectDetectionClass/main_Torch_Parallel.py"

    # Создаем общий список для хранения значений fps
    shared_fps = multiprocessing.Manager().list()

    # Запуск двух процессов одновременно
    process1 = subprocess.Popen(['python', script_path1])
    process2 = subprocess.Popen(['python', script_path2])

    # Ожидание завершения обоих процессов
    process1.wait()
    process2.wait()

    print("Both processes have finished.")
