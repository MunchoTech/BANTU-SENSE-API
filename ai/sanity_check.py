import torch
import transformers
import datasets

print("Torch version:", torch.__version__)
print("Transformers version:", transformers.__version__)
print("Datasets version:", datasets.__version__)

print("CUDA available:", torch.cuda.is_available())
