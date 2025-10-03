import torch
from torchvision import models, transforms
from torchvision.models import ResNet50_Weights
from PIL import Image
from pathlib import Path

# -------------------------------
# CONFIG
# -------------------------------
MODEL_PATH = Path("models/resnet50_finetunedV3.pth")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
NUM_CLASSES = 5  # Replace with your number of species
IDX_TO_CLASS = {0: 'koivu', 1: 'kuusi', 2: 'lehmus', 3: 'pihlaja', 4: 'vaahtera'}  # Replace with your classes

# -------------------------------
# MODEL LOADING
# -------------------------------
def load_model(model_path, num_classes, device):
    # Initialize architecture
    model = models.resnet50(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
    
    # Load trained weights
    model.load_state_dict(torch.load(model_path, map_location=device))
    
    model = model.to(device)
    model.eval()  # important for inference
    return model

# -------------------------------
# IMAGE PREPROCESSING
# -------------------------------
def preprocess_image(img_path):
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
    ])
    img = Image.open(img_path).convert("RGB")
    return transform(img).unsqueeze(0)  # Add batch dimension

# -------------------------------
# PREDICTION
# -------------------------------
def predict_image(model, img_path, idx_to_class, device):
    x = preprocess_image(img_path).to(device)
    with torch.no_grad():
        out = model(x)
        probs = torch.nn.functional.softmax(out, dim=1)
        p, pred = torch.max(probs, dim=1)
    return idx_to_class[int(pred.item())], float(p.item())

# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Predict tree species from an image")
    parser.add_argument("image_path", type=str, help="Path to the image to predict")
    args = parser.parse_args()

    # Load model
    model = load_model(MODEL_PATH, NUM_CLASSES, DEVICE)

    # Predict
    pred_class, probability = predict_image(model, args.image_path, IDX_TO_CLASS, DEVICE)
    print(f"Predicted class: {pred_class}, Probability: {probability:.4f}")
