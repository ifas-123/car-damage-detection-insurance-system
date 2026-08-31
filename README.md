Computer Vision-Based Car Damage Detection and Automated Insurance Cost Estimation System
Project Overview

The Computer Vision-Based Car Damage Detection and Automated Insurance Cost Estimation System is a software engineering project that integrates computer vision, deep learning and automated cost estimation to support the preliminary assessment of vehicle damage for insurance claims.

The system allows policyholders to provide vehicle information and upload images of damaged vehicles. A fine-tuned YOLOv8s object-detection model analyses the uploaded image and identifies supported vehicle-damage categories. The detected damage is then used by the system to generate an estimated repair cost based on the identified damage, estimated damage size and vehicle brand tier.

The system also provides an insurance claim-management workflow through which submitted claims can be reviewed by an insurance assessor.

Key Features
Policyholder registration and authentication
Policyholder login
Vehicle information entry
Vehicle-damage image upload
AI-based vehicle-damage detection
Detection of:
Crack
Dent
Rust
Scratch
Bounding-box visualisation of detected damage
Automated repair-cost estimation
Damage/defect breakdown
Insurance claim submission
Policyholder claim history
Assessor authentication
Active insurance claim management
Individual claim review
Claim approval and rejection
Assessor repair-cost override
Database-based claim persistence
Machine Learning Model

The system uses a fine-tuned YOLOv8s object-detection model for vehicle-damage detection.

The trained model is stored in:

models/best.pt

The model was trained using a vehicle exterior damage dataset containing the following damage classes:

Crack
Dent
Rust
Scratch
Model Validation Results
Metric	Result
Precision	0.5601
Recall	0.3225
mAP@50	0.3089
mAP@50–95	0.1368

The model is intended to provide an automated preliminary damage assessment and does not replace professional insurance assessment.

System Architecture

The main application is implemented using Python and Streamlit.

Policyholder
     │
     ▼
Streamlit Web Application
     │
     ├── Vehicle Information
     │
     ├── Image Upload
     │
     ▼
YOLOv8s Damage Detection
     │
     ├── Crack
     ├── Dent
     ├── Rust
     └── Scratch
     │
     ▼
Automated Cost Estimation
     │
     ▼
Insurance Claim
     │
     ▼
SQLite Database
     │
     ▼
Assessor Portal
Technologies Used
Python
Streamlit
YOLOv8 / Ultralytics
PyTorch
OpenCV
Pillow
NumPy
Pandas
SQLite
Jupyter Notebook
Project Structure
car-damage-detection-system/
│
├── app.py
├── database.py
├── car_damage_detection_system.ipynb
├── requirements.txt
├── README.md
│
├── models/
│   └── best.pt
│
├── uploads/
│   └── .gitkeep
│
└── examples/
File Description
File / Folder	Description
app.py	Main Streamlit application
database.py	Database creation and database-management functions
car_damage_detection_system.ipynb	Dataset preparation, model training, fine-tuning and evaluation
requirements.txt	Python dependencies required to run the application
models/best.pt	Trained YOLOv8s model
uploads/	Runtime location for uploaded images
examples/	Selected example detection outputs
Dataset

The model was trained using the Car Exterior Damage Detection dataset available through Roboflow Universe.

Dataset source:

Car Exterior Damage Detection Dataset – Roboflow Universe

The dataset was used for academic/project development purposes. Please refer to the dataset provider's terms and licensing information before redistributing the dataset itself.

The dataset is not included in this repository.

Installation

Clone the repository:

git clone YOUR_GITHUB_REPOSITORY_URL

Navigate into the project directory:

cd car-damage-detection-system

Create a virtual environment:

python -m venv .venv

Activate the virtual environment.

Windows
.venv\Scripts\activate
macOS / Linux
source .venv/bin/activate

Install the required dependencies:

pip install -r requirements.txt
Running the Application

Run the Streamlit application using:

streamlit run app.py

The application will then provide a local web address that can be opened in a web browser.

Testing

The system was functionally tested using 17 predefined test cases covering:

Registration
Authentication
Vehicle information
Image uploading
AI damage detection
Automated cost estimation
Claim submission
Claim history
Assessor authentication
Claim review
Claim approval
Claim rejection
Cost override
Database persistence

All 17 functional test cases passed successfully, resulting in a 100% functional testing pass rate.

Limitations

The system is a project prototype and has several limitations:

AI detection performance depends on the quality and characteristics of the uploaded image.
The trained model is limited to the damage classes represented in the training dataset.
Automated repair-cost estimates are preliminary estimates rather than official quotations.
Final insurance decisions require human assessor review.
The current implementation is not intended to replace professional vehicle inspection.
Future Improvements

Potential future improvements include:

Increasing the size and diversity of the training dataset
Improving YOLO model accuracy
Adding additional vehicle-damage categories
Integrating real-time repair-price information
Developing a mobile application
Adding secure insurance-company API integration
Implementing stronger authentication and security
Deploying the system using cloud infrastructure
Supporting real-time camera-based damage detection
Academic Project

This repository contains the implementation and supporting machine-learning materials for the final-year Software Engineering project:

Computer Vision-Based Car Damage Detection and Automated Insurance Cost Estimation System
