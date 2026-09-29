from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from ultralytics import YOLO
from PIL import Image
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "best_GabunganFinal.pt"
model = YOLO(MODEL_PATH)

dilindungi_classes = [
    "anoa", "babirusa", "biawak_pohon_biru", "harimau_sumatera",
    "jalak_bali", "kakatua_jambul_kuning", "kera_hitam", "orangutan",
    "owa_jawa", "rusa_bawean", "siamang", "komodo"
]


@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    img_bytes = await file.read()
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    results = model(img)[0]

    if len(results.boxes) == 0:
        return {"hasil": [], "boxes": []}

    hasil = []
    boxes = []

    for box in results.boxes:
        cls_id = int(box.cls[0])
        class_name = results.names[cls_id]
        conf = float(box.conf.item())
        x1, y1, x2, y2 = box.xyxy[0].tolist()

        status = "Langka" if class_name in dilindungi_classes else "Tidak langka"

        hasil.append({
            "hewan": class_name,
            "status": status,
            "confidence": round(conf * 100, 2)
        })

        boxes.append({
            "hewan": class_name,
            "status": status,
            "confidence": round(conf * 100, 2),
            "box": [x1, y1, x2, y2]
        })

    return {"hasil": hasil, "boxes": boxes}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
