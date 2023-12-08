"""
Файл, чтобы посмотреть количество доступной видеопамяти для PyTorch
"""

import torch

if __name__ == '__main__':
    # Получение доступного объема видеопамяти (VRAM)
    if torch.cuda.is_available():
        total_vram = torch.cuda.get_device_properties(0).total_memory
        print(f"Total VRAM: {total_vram / (1024**3):.2f} GB")
    else:
        print("CUDA not available. Check your PyTorch installation and GPU drivers.")