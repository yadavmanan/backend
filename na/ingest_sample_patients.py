# Script to ingest 11 sample patients into the database
from database import add_patient

sample_patients = [
    {"name": "Alice Smith", "age": 45, "sex": "Female", "life_stage": "Perimenopause", "phone": "555-1001", "status": "pending"},
    {"name": "Bob Johnson", "age": 52, "sex": "Male", "life_stage": "Middle Age", "phone": "555-1002", "status": "pending"},
    {"name": "Carol Lee", "age": 38, "sex": "Female", "life_stage": "Premenopause", "phone": "555-1003", "status": "pending"},
    {"name": "David Kim", "age": 60, "sex": "Male", "life_stage": "Senior", "phone": "555-1004", "status": "pending"},
    {"name": "Eva Brown", "age": 29, "sex": "Female", "life_stage": "Reproductive", "phone": "555-1005", "status": "pending"},
    {"name": "Frank Green", "age": 67, "sex": "Male", "life_stage": "Senior", "phone": "555-1006", "status": "pending"},
    {"name": "Grace Hall", "age": 54, "sex": "Female", "life_stage": "Postmenopause", "phone": "555-1007", "status": "pending"},
    {"name": "Henry Young", "age": 41, "sex": "Male", "life_stage": "Middle Age", "phone": "555-1008", "status": "pending"},
    {"name": "Ivy King", "age": 36, "sex": "Female", "life_stage": "Premenopause", "phone": "555-1009", "status": "pending"},
    {"name": "Jackie Chan", "age": 58, "sex": "Male", "life_stage": "Senior", "phone": "555-1010", "status": "pending"},
    {"name": "Karen White", "age": 49, "sex": "Female", "life_stage": "Perimenopause", "phone": "555-1011", "status": "pending"},
]

for patient in sample_patients:
    add_patient(patient)
print("11 sample patients ingested.")
