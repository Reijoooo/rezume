import torch

if __name__ == "__main__":

    pt_model_path = 'E:\GitHubRepository\Dessertation\Video\yolov8n.pt'
    model = torch.load(pt_model_path, map_location=torch.device('cuda'))

    model_id = id(model)

    print(f"ID модели: {model_id}")
