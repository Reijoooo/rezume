"""
Класс для определения объекта на видео
Данный файл просто определяет объекты на RSTP потоке при помощи YOLOv8
Данный файл использует CPU
Для работы требуется прописать:
pip install ultralytics
"""

import cv2
from time import time
import torch.cuda
from ultralytics import YOLO

class ObjectDetection:

    def __init__(self, capture_index):

        self.capture_index = capture_index
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)

        self.model = self.load_model()

    def load_model(self):

        model = YOLO("../../yolov8n.pt")
        model.fuse()

        return model

    def predict(self, frame):

        results = self.model(frame)

        return results

    def plot_bboxes(self, results, frame):

        xyxys = []
        confidences = []
        class_ids = []

        for result in results:
            boxes = result.boxes.cpu().numpy()
            # xyxy = boxes.xyxy

            ## Можно выводить прямоугольники так
            # for xyxy in xyxys:
            #     cv2.rectangle(resize, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (0, 255, 0), 2)

            # А можно так, и в выводе выводить не кадр, а results[0].plot()
            xyxys.append(boxes.xyxy)
            confidences.append(boxes.conf)
            class_ids.append(boxes.cls)

        return results[0].plot(), frame, xyxys, confidences, class_ids

    def __call__(self):

        cap = cv2.VideoCapture(self.capture_index)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Изменение размера кадра до (1280, 720)
            frame = cv2.resize(frame, (1280, 720))

            # Детекция объектов
            with torch.no_grad():
                results = self.predict(frame)

            # Отображение результатов
            plot, frame, xyxys, confidences, class_ids = self.plot_bboxes(results, frame)

            cv2.imshow("Object Detection cpu", plot)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()