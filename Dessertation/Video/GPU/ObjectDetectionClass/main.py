from YOLOv8_func import ObjectDetection

if __name__ == "__main__":

    detector = ObjectDetection(capture_index='https://5e694eade8405.streamlock.net/live/PerekrKrlovaKrProsp.stream/playlist.m3u8')
    detector()
