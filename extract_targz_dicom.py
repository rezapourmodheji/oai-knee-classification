import pandas as pd
import os
import tarfile
import re
import pydicom  # Ensure pydicom is installed: pip install pydicom
import shutil
import time 

# Define paths
study = '/home/reza/oai-knee-classification/'
data_raw = study + 'Data_Raw/'
base_image_path = data_raw + 'images/00m/'
outinfo_path = data_raw + '/output_info/'
scores_path = data_raw + '/scores/'
baseimage_folders = ['0.C.2','0.E.1']


mapping_csv = outinfo_path + 'subject_folder_mapping.csv'
output_base_path = "~/oai-knee-classification/Data_Reduced/dicoms"

# Clear the dicoms folder
shutil.rmtree(os.path.expanduser(output_base_path), ignore_errors=True)


# Load mapping CSV
mapping_df = pd.read_csv(os.path.expanduser(mapping_csv))

# Filter valid subject folders with date folders
valid_df = mapping_df[mapping_df['date_folders'] != 'No date folders found']
print( valid_df['src_subject_id'].nunique())
# valid_df = valid_df.iloc[1:2]


def is_dicom_file(filepath):
    """
    Checks if a given file is a DICOM file.

    Args:
        filepath (str): The path to the file.

    Returns:
        bool: True if the file is a DICOM file, False otherwise.
    """
    try:
        # Attempt to read the DICOM file
        pydicom.dcmread(filepath)
        return True
    except pydicom.errors.InvalidDicomError:
        # If an InvalidDicomError is raised, it's not a valid DICOM file
        return False
    except FileNotFoundError:
        # Handle cases where the file doesn't exist
        print(f"Error: File not found at {filepath}")
        return False
    except Exception as e:
        # Catch other potential errors during file reading
        print(f"An unexpected error occurred: {e}")
        return False

# Function to check if extracted DICOMs are knee images
def is_knee_dicom(extracted_path):
    for file_name in os.listdir(extracted_path):
        # print(file_name)
        dcm_path = os.path.join(extracted_path, file_name)
        try:
            ds = pydicom.dcmread(dcm_path)
            
            # Check BodyPartExamined (0018,0015) for "KNEE"
            body_part = ds.get((0x0018, 0x0015), None)
            study_ID = ds.get((0x0008, 0x0060), None)
            
            if body_part and 'KNEE' in body_part.value.upper() and \
                ('CR' in study_ID.value.upper() or 'DX' in study_ID.value.upper()):
                return True
            # Fallback: Check SeriesDescription (0008,103E) for "knee"
            # series_desc = ds.get((0x0008, 0x103E), None)
            # if series_desc and 'KNEE' in series_desc.value.upper():
            #     return True
        except Exception as e:
            print(f"Error reading DICOM {dcm_path}: {str(e)}")
    
    return False





# Initialize results
extracted_files = []

# Record start time
start_time = time.perf_counter()



# Process each subject
for _, row in valid_df.iterrows():
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

        # Output folder (temporary for extraction)
        temp_out_folder = os.path.expanduser(
            f"{output_base_path}/{subject_id}/{date_folder}_temp"
        )
        os.makedirs(temp_out_folder, exist_ok=True)

        # Extract .tar.gz files
        for file_name in os.listdir(src_folder):
            if file_name.endswith('.tar.gz'):
                tar_path = os.path.join(src_folder, file_name)
                try:
                    with tarfile.open(tar_path, 'r:gz') as tar:
                        tar.extractall(path=temp_out_folder)

                    final_out_folder = os.path.expanduser(
                            f"{output_base_path}/{subject_id}/{date_folder}/{file_name[:-7]}"  # Remove .tar.gz
                        )
                    os.makedirs(os.path.dirname(final_out_folder), exist_ok=True)
                    
                    
                    # Check if it's a knee image
                    if is_knee_dicom(temp_out_folder):
                        # Move to final path if it's knee
                        final_out_folder = os.path.expanduser(
                            f"{output_base_path}/{subject_id}/{date_folder}/{file_name[:-7]}"  # Remove .tar.gz
                        )
                        os.makedirs(os.path.dirname(final_out_folder), exist_ok=True)
                        os.rename(temp_out_folder, final_out_folder)
                        extracted_files.append({
                            'src_subject_id': subject_id,
                            'date_folder': date_folder,
                            'tar_file': file_name,
                            'extracted_path': final_out_folder,
                            'is_knee': True
                        })
                        print(f"Kept knee DICOMs for {subject_id}/{date_folder}/{file_name}")
                    else:
                        # Delete non-knee extraction
                        for root, dirs, files in os.walk(temp_out_folder, topdown=False):
                            for name in files:
                                os.remove(os.path.join(root, name))
                            for name in dirs:
                                os.rmdir(os.path.join(root, name))
                        os.rmdir(temp_out_folder)
                        extracted_files.append({
                            'src_subject_id': subject_id,
                            'date_folder': date_folder,
                            'tar_file': file_name,
                            'extracted_path': 'Deleted (not knee)',
                            'is_knee': False
                        })
                        print(f"Deleted non-knee DICOMs for {subject_id}/{date_folder}/{file_name}")
                except Exception as e:
                    extracted_files.append({
                        'src_subject_id': subject_id,
                        'date_folder': date_folder,
                        'tar_file': file_name,
                        'extracted_path': f"Error: {str(e)}",
                        'is_knee': False
                    })
                    # Clean up temp if error
                    if os.path.exists(temp_out_folder):
                        for root, dirs, files in os.walk(temp_out_folder, topdown=False):
                            for name in files:
                                os.remove(os.path.join(root, name))
                            for name in dirs:
                                os.rmdir(os.path.join(root, name))
                        os.rmdir(temp_out_folder)

# Record end time and calculate runtime
end_time = time.perf_counter()
runtime_seconds = end_time - start_time
runtime_minutes = runtime_seconds / 60
runtime_hours = runtime_minutes / 60


# Save extraction log to CSV
output_df = pd.DataFrame(extracted_files)
output_csv = outinfo_path + 'extraction_log.csv'
output_df.to_csv(os.path.expanduser(output_csv), index=False)


# Print runtime summary
print(f"Saved extraction log with {len(output_df)} entries to {output_csv}")
print(f"Total runtime: {runtime_seconds:.2f} seconds ({runtime_minutes:.2f} minutes, {runtime_hours:.2f} hours)")