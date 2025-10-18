"""
Quick GPU/CUDA check
"""
import torch

print("\n" + "="*70)
print("GPU/CUDA Check")
print("="*70 + "\n")

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU device: {torch.cuda.get_device_name(0)}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    print("\n✅ GPU is available and ready to use!")
    print("Training will use GPU acceleration.")
else:
    print("\n⚠️  CUDA is not available")
    print("Training will use CPU (slower)")
    print("\nPossible reasons:")
    print("1. PyTorch was installed without CUDA support")
    print("2. GPU drivers are not installed or outdated")
    print("3. No compatible NVIDIA GPU found")
    print("\nTo install PyTorch with CUDA support:")
    print("pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")

print("\n" + "="*70 + "\n")
