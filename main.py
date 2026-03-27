import smtplib
import random
import os
import shutil
import uuid
import tensorflow as tf
import numpy as np

from email.mime.text import MIMEText
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from database import SessionLocal, engine, Base
import models
from models import User, Analysis
from schemas import RegisterSchema, LoginSchema
from crud import create_user, authenticate_user

from PIL import Image
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet



# ---------------- CREATE TABLES ----------------
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bone Loss Backend")


# ---------------- DATABASE ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



EMAIL_ADDRESS = "srik29924@gmail.com"
EMAIL_PASSWORD = "jdiz fkzm okyk stng"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

otp_storage = {}


# ---------------- FORGOT PASSWORD ----------------

class ForgotPasswordRequest(BaseModel):
    email: str


@app.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):

    email = data.email.strip().lower()

    user = db.query(User).filter(
        func.lower(User.email) == email
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")

    # Generate OTP
    otp = str(random.randint(100000, 999999))

    # Update fields
    user.otp = otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)
    user.otp_verified = False

    db.add(user)      # make sure SQLAlchemy tracks the update
    db.commit()
    db.refresh(user)

    print("OTP stored in DB:", user.otp)

    subject = "BoneLoss AI Password Reset"
    body = f"Your 6-digit OTP is: {otp}\n\nExpires in 5 minutes."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
    server.quit()

    return {"message": "OTP sent to email"}



class VerifyOTPRequest(BaseModel):
    email: str
    otp: str


@app.post("/verify-otp")
def verify_otp(data: VerifyOTPRequest, db: Session = Depends(get_db)):

    print(models.User.__table__.columns.keys())

    user = db.query(models.User).filter(
        func.lower(models.User.email) == data.email.lower()
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.otp != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if datetime.utcnow() > user.otp_expiry:
        raise HTTPException(status_code=400, detail="OTP expired")

    user.otp_verified = True
    db.commit()

    return {"message": "OTP verified"}




class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str


@app.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(
        func.lower(models.User.email) == data.email.lower()
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.otp_verified:
        raise HTTPException(status_code=400, detail="OTP not verified")

    user.password = pwd_context.hash(data.new_password)

    user.otp = None
    user.otp_expiry = None
    user.otp_verified = False

    db.commit()

    return {"message": "Password reset successful"}


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


# ================= EDIT PROFILE =================
class UpdateProfileSchema(BaseModel):
    full_name: str
    email: str


@app.put("/edit-profile/{user_id}")
def edit_profile(user_id: int, updated_data: UpdateProfileSchema, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.full_name = updated_data.full_name
    user.email = updated_data.email

    db.commit()
    db.refresh(user)

    return {
        "status": "success",
        "message": "Profile updated successfully",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email
        }
    }


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

# ---------------- ANALYTICS ----------------
@app.get("/analytics/{user_id}")
def analytics(user_id: int, db: Session = Depends(get_db)):

    analyses = db.query(Analysis).filter(Analysis.user_id == user_id).all()

    total_cases = len(analyses)

    avg_loss = round(
        sum(a.bone_loss_percent for a in analyses) / total_cases, 2
    ) if total_cases else 0

    accuracy = round(
        sum(a.confidence for a in analyses) / total_cases, 2
    ) if total_cases else 0

    mild = db.query(Analysis).filter(
        Analysis.user_id == user_id,
        Analysis.prediction == "Mild"
    ).count()

    moderate = db.query(Analysis).filter(
        Analysis.user_id == user_id,
        Analysis.prediction == "Moderate"
    ).count()

    severe = db.query(Analysis).filter(
        Analysis.user_id == user_id,
        Analysis.prediction == "Severe"
    ).count()

    return {
        "total_cases": total_cases,
        "avg_loss": avg_loss,
        "accuracy": accuracy,
        "severity_distribution": {
            "mild": mild,
            "moderate": moderate,
            "severe": severe
        }
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

    # Prevent invalid ID
    if analysis_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid analysis ID")

    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "patient_id": analysis.patient_id,
        "severity": analysis.prediction,
        "average_bone_loss": analysis.bone_loss_percent,
        "confidence": analysis.confidence
    }

# ---------------- SAVED CASES ----------------
@app.get("/saved-cases/{user_id}")
def get_saved_cases(user_id: int, db: Session = Depends(get_db)):

    analyses = db.query(Analysis).filter(
        Analysis.user_id == user_id
    ).order_by(Analysis.created_at.desc()).limit(5).all()

    results = []

    for a in analyses:
        results.append({
            "analysis_id": a.id,
            "patient_id": a.patient_id,
            "prediction": a.prediction,
            "bone_loss_percent": a.bone_loss_percent,
            "confidence": a.confidence,
            "created_at": a.created_at
        })

    return results

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

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

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