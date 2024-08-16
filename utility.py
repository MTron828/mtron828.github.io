import os
import shutil
import zipfile

def addNotPresent(arr1, arr2):
    st = set()
    for el in arr1:
        st.add(el)
    for el in arr2:
        if not el in st:
            st.add(el)
            arr1.append(el)
    return arr1

def clear_folder(folder_path):
    # Walk through the directory tree from bottom to top
    for root, dirs, files in os.walk(folder_path, topdown=False):
        # Remove each file
        for name in files:
            file_path = os.path.join(root, name)
            #print(f"Removing file: {file_path}")
            os.remove(file_path)
        # Remove each directory
        for name in dirs:
            dir_path = os.path.join(root, name)
            #print(f"Removing directory: {dir_path}")
            os.rmdir(dir_path)

def copy_folder_contents(src, dst):
    # Ensure the source directory exists
    if not os.path.exists(src):
        #print(f"Source directory {src} does not exist.")
        return
    
    # Ensure the destination directory exists
    if not os.path.exists(dst):
        os.makedirs(dst)
        #print(f"Created destination directory {dst}.")
    
    # Walk through all directories and files in the source directory
    for root, dirs, files in os.walk(src):
        # Determine the path offset for the destination
        rel_path = os.path.relpath(root, src)
        dest_dir = os.path.join(dst, rel_path)
        
        # Ensure each directory in the destination path exists
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            #print(f"Created directory {dest_dir}.")
        
        # Copy each file
        for file in files:
            file_src = os.path.join(root, file)
            file_dst = os.path.join(dest_dir, file)
            shutil.copy2(file_src, file_dst)
            #print(f"Copied {file_src} to {file_dst}.")

def zip_folder(folder_path, output_zip_path):
    # Create a ZIP file at the specified output path
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Calculate the length of the path to remove absolute paths in the ZIP file
        len_dir_path = len(os.path.dirname(folder_path))
        
        # Walk through all directories and files in the folder
        for root, _, files in os.walk(folder_path):
            # Include all files in the folder and subfolders
            for file in files:
                file_path = os.path.join(root, file)
                # Create the relative path for files to maintain the directory structure
                # Relative path inside the ZIP archive
                zip_file_path = file_path[len_dir_path:].strip(os.path.sep)
                zip_file_path = "".join(zip_file_path.split("/tmp"))
                # Debug print to show which files are added
                #print(f"Adding {file_path} as {zip_file_path}")
                
                # Add the file to the ZIP file
                zipf.write(file_path, zip_file_path)