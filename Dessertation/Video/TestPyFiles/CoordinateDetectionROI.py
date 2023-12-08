"""
Данный файл использовать для определения XMIN YMIN и XMAX YMAX значений на камере
Надо, чтобы установить область
Изменить в "cv2.resize" на размер камеры (на всякий чтобы не проебаться со значениями
"""

import cv2

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Coordinates: ({x}, {y})")

if __name__ == '__main__':

    # Загрузка видеопотока с камеры (0 - индекс камеры)
    cap = cv2.VideoCapture('https://5e694eade8405.streamlock.net/live/PlPimenova.stream/playlist.m3u8')

    # Установка обработчика событий мыши
    cv2.namedWindow("Frame")
    cv2.setMouseCallback("Frame", mouse_callback)

    while True:
        ret, frame = cap.read()
        frame = cv2.resize(frame, (1280, 720))
        if not ret:
            break

        # Отображение кадра
        cv2.imshow("Frame", frame)

        # Выход из цикла при нажатии клавиши 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Освобождение ресурсов
    cap.release()
    cv2.destroyAllWindows()
