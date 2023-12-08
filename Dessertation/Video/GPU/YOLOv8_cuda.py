"""
Данный файл просто определяет объекты на RSTP потоке при помощи YOLOv8
Данный файл использует CUDA
Для работы требуется прописать:
pip install ultralytics
"""

import cv2
from time import time
from ultralytics import YOLO

if __name__ == '__main__':

    model = YOLO("../yolov8n.pt")

    cap = cv2.VideoCapture('https://5e694eade8405.streamlock.net/live/PerekrKrlovaKrProsp.stream/playlist.m3u8')

    # Считаем FPS
    start_time = time()
    frame_count = 0

    while cap.isOpened():

        # Чтение кадра
        ret, frame = cap.read()

        if not ret:
            break

        resize = cv2.resize(frame, (1280, 720))

        results = model(resize)

        xyxys = []
        confidences = []
        class_ids = []

        for result in results:
            boxes = result.boxes.cuda()
            # xyxy = boxes.xyxy

            ## Можно выводить прямоугольники так
            # for xyxy in xyxys:
            #     cv2.rectangle(resize, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (0, 255, 0), 2)

            # А можно так, и в выводе выводить не кадр, а results[0].plot()
            xyxys.append(boxes.xyxy)
            confidences.append(boxes.conf)
            class_ids.append(boxes.cls)

        # Рассчитываем FPS
        frame_count += 1
        elapsed_time = time() - start_time
        fps = frame_count / elapsed_time

        cv2.putText(resize, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow('YOLOv8_cuda', results[0].plot())

        # Выход при нажатии клавиши 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Освобождение ресурсов
    cap.release()
    cv2.destroyAllWindows()