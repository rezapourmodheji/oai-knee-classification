import pandas as pd
  import os
  import tarfile
  import re

  # Define paths
  mapping_csv = "~/oai-knee-classification/Data_Raw/subject_date_folder_mapping.csv"
  output_base_path = "~/oai-knee-classification/Data_Processed/dicoms"

  # Create output directory
  os.makedirs(os.path.expanduser(output_base_path), exist_ok=True)

  # Load mapping CSV
  mapping_df = pd.read_csv(os.path.expanduser(mapping_csv))

  # Filter valid subject folders with date folders
  valid_df = mapping_df[mapping_df['date_folders'] != 'No date folders found']

  # Initialize results
  extracted_files = []

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

          # Output folder
          out_folder = os.path.expanduser(
              f"{output_base_path}/{subject_id}/{date_folder}"
          )
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

  # Save extraction log
  log_df = pd.DataFrame(extracted_files)
  log_csv = "~/oai-knee-classification/Data_Processed/extraction_log.csv"
  log_df.to_csv(os.path.expanduser(log_csv), index=False)
  print(f"Saved extraction log to {log_csv}")
  print(f"Extracted {len(log_df[log_df['extracted_path'].str.startswith(output_base_path)])} files")
  print(f"Errors: {len(log_df[~log_df['extracted_path'].str.startswith(output_base_path)])}")