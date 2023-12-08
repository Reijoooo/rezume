"""
Данный файл скринит в plots бъекты, заехавшие в выделенную область при помощи YOLOv8
Данный файл использует CPU
Для работы требуется прописать:
pip install ultralytics
"""

import cv2
from time import time
from ultralytics import YOLO
import matplotlib.pyplot as plt

if __name__ == '__main__':

    model = YOLO("../yolov8n.pt")

    cap = cv2.VideoCapture('https://5e694eade8405.streamlock.net/live/PlPimenova.stream/playlist.m3u8')

    # Определение области интереса (ROI)
    roi_top_left = (156, 369)
    roi_bottom_right = (453, 427)

    # Считаем FPS
    start_time = time()
    frame_count = 0

    q = 0 # Костыль чтобы не делалось 100000000 снимков

    while cap.isOpened():

        # Чтение кадра и изменение размера
        ret, frame = cap.read()
        resize = cv2.resize(frame, (1280, 720))

        if not ret:
            break

        # prediction
        results = model(resize)

        # Отображение области интереса
        cv2.rectangle(resize, roi_top_left, roi_bottom_right, (0, 255, 0), 2)

        xyxyt = []
        xyxys = []
        confidences = []
        class_ids = []

        for result in results:
            boxes = result.boxes.cpu().numpy()
            xyxyt = boxes.xyxy

            ## Можно выводить прямоугольники так
            # for xyxy in xyxys:
            #     cv2.rectangle(resize, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (0, 255, 0), 2)

            # А можно так, и в выводе выводить не кадр, а results[0].plot()
            xyxys.append(boxes.xyxy)
            confidences.append(boxes.conf)
            class_ids.append(boxes.cls)

            for xyxy in xyxyt:

                center_x = (int(xyxy[0]) + int(xyxy[2])) / 2
                center_y = (int(xyxy[1]) + xyxy[3]) / 2

            if q > 8: # Костыль чтобы не делалось 100000000 снимков
                if roi_top_left[0] < center_x < roi_bottom_right[0] and roi_top_left[1] < center_y < roi_bottom_right[1]:
                    q = 0
                    plt.imshow(resize)
                    plt.show()

        q += 1 # Костыль чтобы не делалось 100000000 снимков

        # Рассчитываем FPS
        frame_count += 1
        elapsed_time = time() - start_time
        fps = frame_count / elapsed_time

        cv2.putText(resize, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow('YOLOv8', results[0].plot())

        # Выход при нажатии клавиши 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Освобождение ресурсов
    cap.release()
    cv2.destroyAllWindows()