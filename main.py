from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal, engine, Base
import models
from models import Analysis
from schemas import RegisterSchema, LoginSchema
from crud import create_user, authenticate_user

import os
import shutil
import uuid
import tensorflow as tf
import numpy as np
from PIL import Image
from datetime import datetime, timedelta

import smtplib
from email.mime.text import MIMEText
from passlib.context import CryptContext
import random
from pydantic import BaseModel

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4


# ---------------- CREATE TABLES ----------------
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bone Loss Backend")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- LOAD MODEL ----------------
model = tf.keras.models.load_model("model/bone_loss_model.h5")
classes = ["Mild", "Moderate", "Severe"]

# ---------------- DATABASE ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- FOLDERS ----------------
os.makedirs("uploads", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"message": "Bone Loss FastAPI Backend Running"}

# ---------------- REGISTER ----------------
@app.post("/register")
def register(user: RegisterSchema, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    create_user(db, user)

    return {"status": "success", "message": "Registration successful"}

# ---------------- LOGIN ----------------
@app.post("/login")
def login(user: LoginSchema, db: Session = Depends(get_db)):

    db_user = authenticate_user(db, user.email, user.password)

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    return {
        "status": "success",
        "message": "Login successful",
        "user": {
            "id": db_user.id,
            "full_name": db_user.full_name,
            "email": db_user.email,
            "role": db_user.role
        }
    }

# ---------------- PROFILE ----------------
@app.get("/profile/{user_id}")
def get_profile(user_id: int, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

# ---------------- DASHBOARD ----------------
@app.get("/dashboard/{user_id}")
def dashboard(user_id: int, db: Session = Depends(get_db)):

    analyses = db.query(Analysis).filter(Analysis.user_id == user_id).all()

    total_cases = len(analyses)

    avg_confidence = round(
        sum(a.confidence for a in analyses) / total_cases, 2
    ) if total_cases else 0

    return {
        "total_cases": total_cases,
        "average_confidence": avg_confidence
    }

# ---------------- IMAGE PREPROCESS ----------------
def preprocess_image(image_path):

    img = Image.open(image_path)
    img = img.convert("RGB")
    img = img.resize((224, 224))

    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    return img_array

# ---------------- UPLOAD XRAY ----------------
@app.post("/upload-xray")
async def upload_xray(
    patient_id: str = Form(...),
    user_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    filename = f"{uuid.uuid4()}.jpg"
    file_path = os.path.join("uploads", filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    processed_image = preprocess_image(file_path)

    prediction_probs = model.predict(processed_image, verbose=0)

    predicted_class_index = int(np.argmax(prediction_probs))
    prediction = classes[predicted_class_index]

    confidence = round(float(np.max(prediction_probs)) * 100, 2)

    # -------- HEATMAP --------
    teeth_numbers = [11,12,13,14,21,22,23,24]
    heatmap = []

    for t in teeth_numbers:
        loss = round(np.random.uniform(10,55),2)
        heatmap.append({"tooth":t,"bone_loss_percent":loss})

    avg_bone_loss = round(
        sum(x["bone_loss_percent"] for x in heatmap)/len(heatmap),2
    )

    analysis = Analysis(
        user_id=user_id,
        patient_id=patient_id,
        image_path=file_path,
        prediction=prediction,
        confidence=confidence,
        bone_loss_percent=avg_bone_loss,
        created_at=datetime.utcnow()
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return {
        "analysis_id": analysis.id,
        "prediction": prediction,
        "confidence": confidence,
        "average_bone_loss": avg_bone_loss,
        "heatmap": heatmap
    }

# ---------------- CLINICAL INTERPRETATION ----------------
@app.get("/clinical-interpretation/{analysis_id}")
def clinical_interpretation(analysis_id: int, db: Session = Depends(get_db)):

    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "prediction": analysis.prediction,
        "average_bone_loss": analysis.bone_loss_percent
    }

# ---------------- FULL REPORT ----------------
@app.get("/full-report/{analysis_id}")
def full_report(analysis_id: int, db: Session = Depends(get_db)):

    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "patient_id": analysis.patient_id,
        "severity": analysis.prediction,
        "average_bone_loss": analysis.bone_loss_percent,
        "confidence": analysis.confidence
    }

# ---------------- HISTORY ----------------
@app.get("/history/{user_id}")
def history(user_id: int, db: Session = Depends(get_db)):

    analyses = db.query(Analysis).filter(
        Analysis.user_id == user_id
    ).order_by(Analysis.created_at.desc()).all()

    return analyses

# ---------------- EXPORT PDF ----------------
@app.get("/export-pdf/{analysis_id}")
def export_pdf(analysis_id: int, db: Session = Depends(get_db)):

    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id
    ).first()

    file_path = f"reports/report_{analysis_id}.pdf"

    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    elements = [
        Paragraph("BoneLoss AI Report", styles["Title"]),
        Paragraph(f"Prediction: {analysis.prediction}", styles["Normal"]),
        Paragraph(f"Confidence: {analysis.confidence}", styles["Normal"]),
        Paragraph(f"Bone Loss: {analysis.bone_loss_percent}", styles["Normal"]),
    ]

    doc.build(elements)

    return FileResponse(file_path)