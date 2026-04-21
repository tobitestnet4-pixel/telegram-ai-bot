import zipfile
import os
from pathlib import Path

project_dir = Path(r'C:\Users\HP\Desktop\Telegram_AI_Project')
backup_path = Path(r'C:\Users\HP\Desktop\Telegram_AI_Project_Backup.zip')

# Directories to skip
skip_dirs = {'tportable-x64.6.7.6', '__pycache__', '.qodo', '.git', 'venv', 'env'}

with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(project_dir):
        # Skip unwanted directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            file_path = Path(root) / file
            arcname = file_path.relative_to(project_dir.parent)
            zipf.write(file_path, arcname)

print(f'Backup created: {backup_path}')
print(f'Size: {backup_path.stat().st_size / (1024*1024):.2f} MB')
