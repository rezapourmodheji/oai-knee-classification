import pandas as pd
import os
import tarfile
import re

# Define paths
study = '/home/reza/oai-knee-classification/'
data_raw = study + 'Data_Raw/'
base_image_path = data_raw + 'images/00m/'
outinfo_path = data_raw + '/output_info/'
scores_path = data_raw + '/scores/'
baseimage_folders = ['0.C.2', '0.E.1']

mapping_csv = outinfo_path + 'subject_folder_mapping.csv'
output_base_path = "~/oai-knee-classification/Data_Processed/dicoms"

# Load mapping CSV
mapping_df = pd.read_csv(os.path.expanduser(mapping_csv))

# Filter valid subject folders with date folders
valid_df = mapping_df[mapping_df['date_folders'] != 'No date folders found']

# For testing, use a subset; remove or adjust as needed
subset_df = valid_df.iloc[1:11]

# Initialize results
extracted_files = []

# Function to identify knee .jpg files (placeholder)
def is_knee_jpg(file_name, src_folder):
    # Placeholder: Assume .jpg is a knee image for now
    # Replace with actual logic (e.g., classifier or manual labels)
    # For example, check if file_name ends with '_1x1.jpg' or '_2x2.jpg'
    return file_name.lower().endswith(('_1x1.jpg', '_2x2.jpg'))

# Process each subject
for _, row in subset_df.iterrows():
    subject_id = str(row['src_subject_id']).strip()
    subject_folder_path = row['subject_folder_path']
    date_folders = row['date_folders'].split(',')

    for date_folder in date_folders:
        if not re.match(r'^\d{8}$', date_folder):
            continue  # Skip invalid dates

        # Source folder
        src_folder = os.path.join(subject_folder_path, date_folder)
        if not os.path.exists(src_folder):
            continue

        # Find .jpg files that are likely knee images
        jpg_files = [f for f in os.listdir(src_folder) if is_knee_jpg(f, src_folder)]
        
        for jpg_file in jpg_files:
            # Derive corresponding .tar.gz name (remove _1x1 or _2x2)
            base_name = re.sub(r'(_1x1|_2x2)\.jpg$', '', jpg_file, flags=re.IGNORECASE)
            tar_file = f"{base_name}.tar.gz"
            tar_path = os.path.join(src_folder, tar_file)

            if not os.path.exists(tar_path):
                extracted_files.append({
                    'src_subject_id': subject_id,
                    'date_folder': date_folder,
                    'jpg_file': jpg_file,
                    'tar_file': tar_file,
                    'extracted_path': 'No matching .tar.gz found',
                    'is_knee': False
                })
                continue

            # Output folder
            out_folder = os.path.expanduser(
                f"{output_base_path}/{subject_id}/{date_folder}/{base_name}"
            )
            os.makedirs(out_folder, exist_ok=True)

            # Extract .tar.gz
            try:
                with tarfile.open(tar_path, 'r:gz') as tar:
                    tar.extractall(path=out_folder)
                extracted_files.append({
                    'src_subject_id': subject_id,
                    'date_folder': date_folder,
                    'jpg_file': jpg_file,
                    'tar_file': tar_file,
                    'extracted_path': out_folder,
                    'is_knee': True  # Based on .jpg being identified as knee
                })
                print(f"Extracted knee DICOMs for {subject_id}/{date_folder}/{tar_file} based on {jpg_file}")
            except Exception as e:
                extracted_files.append({
                    'src_subject_id': subject_id,
                    'date_folder': date_folder,
                    'jpg_file': jpg_file,
                    'tar_file': tar_file,
                    'extracted_path': f"Error: {str(e)}",
                    'is_knee': False
                })
                # Clean up if extraction fails
                if os.path.exists(out_folder):
                    for root, dirs, files in os.walk(out_folder, topdown=False):
                        for name in files:
                            os.remove(os.path.join(root, name))
                        for name in dirs:
                            os.rmdir(os.path.join(root, name))
                    os.rmdir(out_folder)

# Save extraction log to CSV
output_df = pd.DataFrame(extracted_files)
output_csv = outinfo_path + 'extraction_log.csv'
output_df.to_csv(os.path.expanduser(output_csv), index=False)
print(f"Saved extraction log with {len(output_df)} entries to {output_csv}")

# Summary
print(f"Total .jpg files processed: {len([r for r in extracted_files if 'jpg_file' in r])}")
print(f"Successful extractions: {len([r for r in extracted_files if r.get('is_knee', False)])}")
print(f"Failed or missing .tar.gz: {len([r for r in extracted_files if not r.get('is_knee', False)])}")
exit(1)
# Process each subject
for _, row in subset_df.iterrows():
    subject_id = str(row['src_subject_id']).strip()
    subject_folder_path = row['subject_folder_path']
    date_folders = row['date_folders'].split(',')

    for date_folder in date_folders:
        if not re.match(r'^\d{8}$', date_folder):
            continue  # Skip invalid dates

        # Source folder
        src_folder = os.path.join(subject_folder_path, date_folder)
        if not os.path.exists(src_folder):
            continue

        
        # Output folder
        out_folder = os.path.expanduser(
            f"{output_base_path}/{subject_id}/{date_folder}"
        )
        print(out_folder)
        os.makedirs(out_folder, exist_ok=True)

        # Extract .tar.gz files
        for file_name in os.listdir(src_folder):
            if file_name.endswith('.tar.gz'):
                tar_path = os.path.join(src_folder, file_name)
                try:
                    with tarfile.open(tar_path, 'r:gz') as tar:
                        tar.extractall(path=out_folder)
                    extracted_files.append({
                        'src_subject_id': subject_id,
                        'date_folder': date_folder,
                        'tar_file': file_name,
                        'extracted_path': out_folder
                    })
                except Exception as e:
                    extracted_files.append({
                        'src_subject_id': subject_id,
                        'date_folder': date_folder,
                        'tar_file': file_name,
                        'extracted_path': f"Error: {str(e)}"
                    })