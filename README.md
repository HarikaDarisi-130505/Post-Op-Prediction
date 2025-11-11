**Post-Operative Patient Recovery Prediction System**

This project is a **web-based healthcare monitoring system** that predicts a **patient’s recovery status** after surgery as **Stable**, **Observe**, or **Critical** using a **Machine Learning model**.
It also provides **OCR-based automatic data extraction** and sends **alerts to doctors** through **Telegram** in case of critical conditions.

---
🔗 **Live Demo:** https://post-op-prediction.onrender.com/
### ⭐ **Features**

* ✔️ Predict patient recovery condition using **Random Forest Classifier**
* ✔️ **OCR (Camera / Image)** to auto-fill patient vitals from medical documents
* ✔️ **Telegram Alerts** for critical/abnormal cases
* ✔️ **Patient Record Management** using SQLite database
* ✔️ **Recovery Trend Graphs** for each patient
* ✔️ Responsive UI using **HTML, CSS, JavaScript**

---

### 🔧 **Tech Stack**

| Component     | Used                                    |
| ------------- | --------------------------------------- |
| Backend       | Python, Flask                           |
| Frontend      | HTML, CSS, JavaScript                   |
| Database      | SQLite                                  |
| ML Model      | Random Forest Classifier (scikit-learn) |
| OCR           | Tesseract OCR / Tesseract.js            |
| Notifications | Telegram Bot API                        |
| Deployment    | Render / Local                          |

---

### 📁 **Project Structure**

```
📦 Post-Op-Recovery
├── app.py                    # Main Flask Application
├── post_op_recovery_model.joblib  # Trained ML Model
├── patients.db               # SQLite Database
├── train.py                  # Model Training Script
├── templates/
│   ├── form3.html            # Patient Input Form (with OCR camera)
│   ├── result1.html          # Prediction Result Page
│   ├── records.html          # Patient Records Page
│   ├── edit.html             # Edit Patient Records
│   └── patient_history.html  # Graph View
└── static/
    └── images/               # Logo & Background Images
```

---

### 🚀 **How to Run Locally**

#### 1️⃣ Install Requirements

```
pip install -r requirements.txt
```

#### 2️⃣ (Optional) Retrain Model

```
python train.py
```

#### 3️⃣ Create / Initialize Database

```
python create_db.py
```

#### 4️⃣ Run the Application

```
python app.py
```

Then open your browser:

```
http://127.0.0.1:5000/
```

---

### 🤖 **Telegram Alert Setup**

1. Open **Telegram**
2. Search for **@BotFather**
3. Create a new bot → get **BOT TOKEN**
4. Search **@userinfobot** → get your **CHAT ID**
5. Add both in `app.py`:

```python
TELEGRAM_BOT_TOKEN = "your_token_here"
TELEGRAM_CHAT_ID = "your_chat_id_here"
```

---

### 📷 **OCR Camera Support**

* Works **locally** using system camera
* For cloud deployment → uses **Tesseract.js** (browser-based OCR)

---

### 🌍 **Deployment Guide (Render)**

1. Upload project to GitHub
2. Create a **New Web Service** in Render
3. Build command (auto):

```
pip install -r requirements.txt
```

4. Start command:

```
gunicorn app:app
```

---

### 🎓 **Project Purpose**

This system improves **post-surgery monitoring** by:

* Reducing manual data entry
* Helping doctors react faster to critical changes
* Keeping consistent medical history records

---

### 💡 **Future Enhancements**

* Add login for hospital admin & staff
* Support multiple patient wards
* Dashboard analytics for patient trends

---


