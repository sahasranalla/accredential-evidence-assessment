import os
import zipfile

def make_zip():
    source_dir = r"c:\Users\P Keerthi\Downloads\nexus-main\nexus-main\nexus-investigation-agent"
    output_zips = [
        r"c:\Users\P Keerthi\Downloads\nexus-main\nexus-main\ACCREDIA_COMPLETE_FINAL.zip",
        r"c:\Users\P Keerthi\Downloads\ACCREDIA_COMPLETE_FINAL.zip"
    ]
    
    exclude_dirs = {"node_modules", "venv", ".venv", "__pycache__", ".git", ".gemini"}
    exclude_extensions = {".pyc", ".pyo"}

    print(f"Creating zip archive from: {source_dir}")
    
    # We will write to the first path, then copy to the second
    primary_zip = output_zips[0]
    
    file_count = 0
    total_bytes = 0
    
    with zipfile.ZipFile(primary_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Exclude unwanted directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in exclude_extensions:
                    continue
                
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, source_dir)
                
                # Prepend the root folder name inside the zip
                archive_name = os.path.join("accredia-project", rel_path)
                
                zipf.write(full_path, archive_name)
                file_count += 1
                total_bytes += os.path.getsize(full_path)

        # Also add the top-level launcher batch script
        top_launcher = r"c:\Users\P Keerthi\Downloads\nexus-main\nexus-main\START_NEXUS.bat"
        if os.path.exists(top_launcher):
            zipf.write(top_launcher, "START_ACCREDIA.bat")

    # Copy to the second output zip (Downloads root)
    import shutil
    try:
        shutil.copy2(primary_zip, output_zips[1])
        print(f"Copied to: {output_zips[1]}")
    except Exception as e:
        print(f"Warning copying to Downloads root: {e}")

    zip_size_mb = os.path.getsize(primary_zip) / (1024 * 1024)
    print(f"SUCCESS: Zipped {file_count} files ({total_bytes / (1024*1024):.2f} MB uncompressed) into:")
    print(f"-> {primary_zip} ({zip_size_mb:.2f} MB)")

if __name__ == "__main__":
    make_zip()
