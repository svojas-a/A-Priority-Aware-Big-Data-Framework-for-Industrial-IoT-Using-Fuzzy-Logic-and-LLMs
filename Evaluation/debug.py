import csv

with open("industrial_fault_detection_training_10000.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    print(reader.fieldnames)