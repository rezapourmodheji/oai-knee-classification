import os

study = '/home/reza/oai-knee-classification/'
data_raw = study + 'Data_Raw/'

def find_common_folder_number(folder1_path, folder2_path):
    # Get list of folder names in each directory
    folders1 = {f for f in os.listdir(folder1_path) if os.path.isdir(os.path.join(folder1_path, f))}
    folders2 = {f for f in os.listdir(folder2_path) if os.path.isdir(os.path.join(folder2_path, f))}
    
    # Find common folder names
    common = folders1.intersection(folders2)

    print(len(folders1))
    print(len(folders2))
    print(len(folders1)+len(folders2))
    
    # Filter for numeric folder names
    common_numbers = [f for f in common if f.isdigit()]
    print(common_numbers)
    
    return common_numbers

# Example usage
C2 = data_raw + 'images/00m/0.C.2/'
E1 = data_raw + 'images/00m/0.E.1/'
common_folders = find_common_folder_number(C2, E1)

if common_folders:
    print(f"Common numeric folder(s): {common_folders}")
else:
    print("No common numeric folders found.")