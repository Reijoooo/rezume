"""
Не хочешь ребутать комп, то НЕ ЗАПУСКАЙ ЭТУ ЕБАНИНУ, ЗАХАВАЕТ ВСЮ ОПЕРАТИВКУ И ВСЁ ЛЯЖЕТ
"""

import cv2
import numpy as np
from torch.multiprocessing import Process, Queue
from ultralytics import YOLO
import torch

class ObjectDetection:

    def __init__(self, capture_index):
        self.capture_index = capture_index
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)

        self.model = self.load_model().to(self.device)

    def load_model(self):
        model = YOLO("../../yolov8n.pt")
        model.fuse()
        # # Получим id объекта (адрес в памяти) модели
        # model_id = id(model)
        #
        # # Выведем id модели
        # print(f"ID модели: {model_id}")
        return model

    def predict(self, frame):
        results = self.model(frame)
        return results

    def plot_bboxes(self, results, frame):
        xyxys = []
        confidences = []
        class_ids = []

        for result in results:
            boxes = result.boxes
            xyxys.append(boxes.xyxy)
            confidences.append(boxes.conf)
            class_ids.append(boxes.cls)

        return results[0].plot(), frame, xyxys, confidences, class_ids

    def process_frames(self, frames):
        for frame in frames:
            frame = cv2.resize(frame, (640, 640)).astype('float32') / 255.0
            frame = torch.from_numpy(frame).permute(2, 0, 1).unsqueeze(0).to(self.device)

            with torch.no_grad():
                results = self.predict(frame)

            plot, _, _, _, _ = self.plot_bboxes(results, frame)
            cv2.imshow("Object Detection cuda", plot)

    def __call__(self):
        cap = cv2.VideoCapture(self.capture_index)

        frames = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frames.append(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()