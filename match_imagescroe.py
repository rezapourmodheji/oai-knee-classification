import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sns
import os
import re
sns.set()

study = '/home/reza/oai-knee-classification/'
data_raw = study + 'Data_Raw/'
base_image_path = data_raw + 'images/00m/'
outinfo_path = data_raw + '/output_info/'
scores_path = data_raw + '/scores/'
baseimage_folders = ['0.C.2','0.E.1']

# Load CSV
df_scores = pd.read_csv(scores_path + 'v00_womac_koos.csv', low_memory=False) # baseline scores

# Ensure required columns exist
if 'src_subject_id' not in df_scores.columns or 'interview_date' not in df_scores.columns:
    print("Error: 'src_subject_id' or 'interview_date' column missing.")
    exit(1)

# Function to validate date folder (YYYYMMDD format, e.g., 20040709)
def is_date_folder(folder_name):
    return bool(re.match(r'^\d{8}$', folder_name))  # 8 digits


# Initialize results
results = []

# Process each subject
for _, row in df_scores.iterrows():
    subject_id = str(row['src_subject_id']).strip()  # Ensure string, remove whitespace

    # Check both 0.C.2 and 0.E.1 for the subject folder
    found_subject = False
    for folder in baseimage_folders:
        subject_folder_path = os.path.expanduser(f"{base_image_path}/{folder}/{subject_id}")
        if os.path.exists(subject_folder_path):
            # Get date subfolders
            date_folders = [
                subfolder for subfolder in os.listdir(subject_folder_path)
                if os.path.isdir(os.path.join(subject_folder_path, subfolder)) and is_date_folder(subfolder)
            ]
            date_folders_str = ','.join(sorted(date_folders)) if date_folders else 'No date folders found'

            results.append({
                'src_subject_id': subject_id,
                'subject_folder_path': subject_folder_path,
                'date_folders': date_folders_str
            })
            found_subject = True
            break

    if not found_subject:
        results.append({
            'src_subject_id': subject_id,
            'subject_folder_path': 'Subject folder not found',
            'date_folders': 'N/A'
        })

print(results[3]['date_folders'].split(',')[0])
# Save results to CSV
output_df = pd.DataFrame(results)
output_csv = outinfo_path + 'subject_folder_mapping.csv'
output_df.to_csv(os.path.expanduser(output_csv), index=False)
print(f"Saved {len(output_df)} mappings to {output_csv}")

# Summary
print(f"Found subject folders: {len(output_df[output_df['subject_folder_path'].str.startswith(base_image_path)])}")
print(f"Missing subject folders: {len(output_df[output_df['subject_folder_path'] == 'Subject folder not found'])}")
print(f"With date folders: {len(output_df[(output_df['date_folders'] != 'No date folders found') & (output_df['date_folders'] != 'N/A')])}")