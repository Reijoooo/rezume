import cv2
import numpy as np
import onnxruntime
from ultralytics import YOLO
from time import time

if __name__ == '__main__':

    # Путь к файлу ONNX модели
    onnx_model = YOLO("yolov8n.onnx")

    # Загрузка ONNX модели
    onnx_session = onnxruntime.InferenceSession(onnx_model)

    # Загрузка видеопотока
    video_capture = cv2.VideoCapture('https://5e694eade8405.streamlock.net/live/PerekrKrlovaKrProsp.stream/playlist.m3u8')  # Замените путь на свой видеофайл

    # Считаем FPS
    start_time = time()
    frame_count = 0

    while True:
        # Считывание кадра из видеопотока
        ret, frame = video_capture.read()
        if not ret:
            break

        # Подготовка кадра для анализа
        input_blob = cv2.dnn.blobFromImage(frame, 1.0 / 255.0, (416, 416), swapRB=True, crop=False)

        # Запуск модели на кадре
        onnx_inputs = {onnx_session.get_inputs()[0].name: input_blob}
        onnx_outputs = onnx_session.run(None, onnx_inputs)

        # Обработка результатов
        detection_results = onnx_outputs[0]

        xyxys = []
        confidences = []
        class_ids = []

        for result in detection_results:
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

        cv2.putText(detection_results, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow('YOLOv8_cuda', detection_results[0].plot())

        # Отображение результата
        cv2.imshow('YOLO Object Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Освобождение ресурсов
    video_capture.release()
    cv2.destroyAllWindows()
