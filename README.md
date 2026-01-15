# 📊 Aadhaar Analytics Dashboard

An interactive full-stack application for visualizing Aadhaar enrolment and update trends. This project combines a **FastAPI** backend for robust data management and a **Streamlit** frontend for a premium analytical experience.

## 🚀 Features

### 📂 Multi-Dataset Support [NEW]
- **Three Datasets**: Seamlessly switch between **Aadhaar Enrolment**, **Demographic Updates**, and **Biometric Updates**.
- **Unified Interface**: The dashboard dynamically adapts charts, KPIs, and filters based on the active dataset.

### 📈 Real-time Analytics
- **Dynamic KPIs**: View total counts, age group breakdowns, and top-performing locations (State vs. District).
- **Trend Analysis**: Interactive time-series charts showing daily trends for the selected dataset.
- **Geographic Insights**: Drill down from National -> State -> District level data.
- **Anomaly Detection**: Automatic identification of low activity days to flag potential data or operational issues.

### 🗺️ Advanced Filtering
- **Smart Filters**: Select a State to see its Districts. Charts automatically update to show data for that specific region.
- **Dynamic Top Location**: 
  - Viewing All? See the **Top State**.
  - Viewing a State? See the **Top District** in that state.

### 🔄 Data Management
- **Local Data Sync [NEW]**: One-click sync to ingest all CSV files from your local dataset folders (`api_data_aadhar_*`).
- **CSV Upload**: Bulk ingest data via CSV files manually.
- **Data Isolation**: Clear and manage data independently for each dataset type.

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) + [Plotly](https://plotly.com/)
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) + [SQLAlchemy](https://www.sqlalchemy.org/)
- **Database**: SQLite (local)
- **Data Source**: Local CSV Datasets & Official Aadhaar Open Data API

## ⚙️ Setup & Installation

### 1. Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd aadhar-hackathon

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## 🏃 Running the Application

For the best experience, run both the backend and frontend simultaneously:

### Start the Backend (API)
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Navigate to `http://127.0.0.1:8000/docs` to view the interactive API documentation.

### Start the Frontend (Dashboard)
```bash
streamlit run frontend/dashboard.py
```
The dashboard will be available at `http://localhost:8501`.

## 📂 Project Structure

- `app/`: FastAPI application logic.
  - `services/`: Core logic for ingestion and analytics.
  - `models.py`: Database schema definitions for Enrolment, Demographic, and Biometric data.
- `frontend/`: Streamlit dashboard code (`dashboard.py`).
- `testing/`: Verification scripts.

---
*Developed for the Aadhaar Analytics Hackathon.*
