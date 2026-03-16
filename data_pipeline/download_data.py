"""
CricketIQ Data Pipeline — Download Script (IPL + T20I only).

Downloads subset archives from Cricsheet and extracts JSON files into data/raw/.
"""
import os
import zipfile
import requests
import logging
from pathlib import Path
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
DATA_DIR = PROJECT_ROOT / "data"

# Only download IPL and T20I male datasets (≈20 MB total vs 500 MB full archive)
DATASETS = {
    "ipl":  "https://cricsheet.org/downloads/ipl_json.zip",
    "t20i": "https://cricsheet.org/downloads/t20s_male_json.zip",
}


def download_file(url: str, output_path: Path) -> None:
    """Download a file with a progress bar."""
    logging.info(f"Downloading {output_path.name} from {url}...")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get("content-length", 0))

    with open(output_path, "wb") as f, tqdm(
        desc=output_path.name, total=total_size,
        unit="iB", unit_scale=True, unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(1024 * 1024):
            f.write(chunk)
            bar.update(len(chunk))

    logging.info(f"Downloaded {output_path.name}.")


def extract_json_files(zip_path: Path, output_dir: Path) -> int:
    """Extract only JSON files from a zip archive. Returns count."""
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(zip_path, "r") as archive:
        json_files = [f for f in archive.namelist() if f.endswith(".json")]
        for name in tqdm(json_files, desc=f"Extracting {zip_path.name}"):
            archive.extract(name, output_dir)
            count += 1
    return count


def main():
    total = 0
    for label, url in DATASETS.items():
        zip_path = DATA_DIR / f"{label}_json.zip"
        if not zip_path.exists():
            download_file(url, zip_path)
        else:
            logging.info(f"{zip_path.name} already exists, skipping download.")

        n = extract_json_files(zip_path, RAW_DATA_DIR)
        total += n
        logging.info(f"{label.upper()}: extracted {n} JSON files.")

    logging.info(f"Done — {total} total match files in {RAW_DATA_DIR}")


if __name__ == "__main__":
    main()
