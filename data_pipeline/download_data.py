"""
CricketIQ Data Pipeline - Download Script.

Downloads the all_json.zip dataset from Cricsheet, extracts JSON files,
and stores them sequentially inside data/raw/.
"""
import os
import zipfile
import requests
import logging
from pathlib import Path
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Constants
CRICSHEET_URL = "https://cricsheet.org/downloads/all_json.zip"
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
ZIP_PATH = PROJECT_ROOT / "data" / "all_json.zip"

def download_file(url: str, output_path: Path) -> None:
    """Download a file with a progress bar."""
    logging.info(f"Downloading dataset from {url}...")
    
    # Ensure parent dir exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024 * 1024  # 1 MB

    with open(output_path, "wb") as file, tqdm(
        desc=output_path.name,
        total=total_size,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for data in response.iter_content(block_size):
            size = file.write(data)
            progress_bar.update(size)
    
    logging.info("Download completed.")

def extract_json_files(zip_path: Path, output_dir: Path) -> None:
    """Extract only JSON files from the zip archive to the output directory."""
    logging.info(f"Extracting JSON files to {output_dir}...")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    extracted_count = 0
    with zipfile.ZipFile(zip_path, 'r') as archive:
        # Get list of all json files inside the archive
        json_files = [f for f in archive.namelist() if f.endswith('.json')]
        
        for file in tqdm(json_files, desc="Extracting"):
            archive.extract(file, output_dir)
            extracted_count += 1
            
    logging.info(f"Successfully extracted {extracted_count} JSON files.")

def main():
    """Main execution block."""
    try:
        if not ZIP_PATH.exists():
            download_file(CRICSHEET_URL, ZIP_PATH)
        else:
            logging.info(f"Zip file already exists at {ZIP_PATH}, skipping download.")
            
        extract_json_files(ZIP_PATH, RAW_DATA_DIR)
        
        # Clean up the zip file to save space (optional)
        # logging.info("Removing zip file...")
        # ZIP_PATH.unlink(missing_ok=True)
        
        logging.info("Data download pipeline finished successfully.")
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")

if __name__ == "__main__":
    main()
