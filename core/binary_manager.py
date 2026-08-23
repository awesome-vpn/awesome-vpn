import logging
import os
import platform
import tarfile
import time

import requests

logger = logging.getLogger(__name__)


class BinaryManager:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.bin_dir = os.path.join(self.base_dir, "bin")
        self.sing_box_path = None

    def get_singbox_path(self):
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Bin directory: {self.bin_dir}")

        if not os.path.exists(self.bin_dir):
            logger.info(f"Creating bin directory: {self.bin_dir}")
            try:
                os.makedirs(self.bin_dir, exist_ok=True)
                logger.info("Successfully created bin directory")
            except OSError as e:
                logger.error(f"Failed to create bin directory: {e}")
                return None

        system = platform.system().lower()
        machine = platform.machine().lower()

        if machine == "x86_64":
            machine = "amd64"
        elif machine == "aarch64":
            machine = "arm64"

        binary_name = f"sing-box-{system}-{machine}"
        sing_box_path = os.path.join(self.bin_dir, binary_name)

        logger.info(f"Looking for sing-box at: {sing_box_path}")

        if os.path.exists(sing_box_path):
            logger.info(f"Using existing sing-box binary: {sing_box_path}")
            self.sing_box_path = sing_box_path
            return sing_box_path

        logger.info(f"sing-box binary ({binary_name}) not found. Attempting to download...")

        version = self._get_latest_version()
        if not version:
            version = os.getenv("SING_BOX_VERSION", "1.13.3").lstrip("v")
            logger.info(f"Could not fetch latest version, using fallback: {version}")
        else:
            logger.info(f"Latest sing-box version: {version}")

        url = self._get_download_url(version, system, machine)

        if url:
            logger.info(f"Download URL: {url}")
            success = self._download_with_retry(url, sing_box_path, binary_name)
            if success:
                self.sing_box_path = sing_box_path
                return sing_box_path

        logger.error(
            f"Auto-download failed. Please install sing-box manually to 'bin/{binary_name}'"
        )
        return None

    def _get_latest_version(self):
        pinned = os.getenv("SING_BOX_VERSION")
        if pinned:
            return pinned.lstrip("v")
        try:
            api_url = "https://api.github.com/repos/SagerNet/sing-box/releases/latest"
            headers = {"Accept": "application/vnd.github.v3+json"}
            resp = requests.get(api_url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                tag_name = data.get("tag_name", "")
                if tag_name.startswith("v"):
                    return tag_name[1:]
                return tag_name
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch latest version: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error fetching version: {e}")
        return None

    def _get_download_url(self, version, system, machine):
        base_url = f"https://github.com/SagerNet/sing-box/releases/download/v{version}"

        if system == "darwin":
            if machine == "arm64":
                return f"{base_url}/sing-box-{version}-darwin-arm64.tar.gz"
            else:
                return f"{base_url}/sing-box-{version}-darwin-amd64.tar.gz"
        elif system == "linux":
            if machine == "amd64":
                return f"{base_url}/sing-box-{version}-linux-amd64.tar.gz"
            elif machine == "arm64":
                return f"{base_url}/sing-box-{version}-linux-arm64.tar.gz"

        return None

    def _download_with_retry(self, url, target_path, binary_name, max_retries=3):
        for attempt in range(max_retries):
            try:
                logger.info(f"Downloading sing-box (attempt {attempt + 1}/{max_retries})...")

                # Test network connectivity first (non-fatal)
                try:
                    test_resp = requests.get("https://github.com", timeout=5)
                    logger.debug(f"GitHub connectivity test: HTTP {test_resp.status_code}")
                except requests.RequestException:
                    logger.debug("GitHub connectivity test failed, continuing anyway")

                resp = requests.get(url, stream=True, timeout=120)
                logger.info(f"Download response status: {resp.status_code}")

                if resp.status_code != 200:
                    logger.warning(f"Download failed: HTTP {resp.status_code}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    return False

                tar_path = os.path.join(self.bin_dir, f"{binary_name}.tar.gz")
                total_size = int(resp.headers.get("content-length", 0))
                if total_size:
                    logger.info(f"Expected file size: {total_size} bytes")
                downloaded = 0

                with open(tar_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if not chunk:
                            continue
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0 and downloaded % (1024 * 1024) == 0:
                            percent = (downloaded / total_size) * 100
                            logger.debug(f"Downloading: {percent:.1f}%")

                logger.info(f"Download complete ({downloaded} bytes). Verifying...")
                if not os.path.exists(tar_path):
                    logger.error(f"Tar file not created: {tar_path}")
                    return False

                logger.info("Extracting...")
                # Safe extraction: only extract the sing-box binary, prevent path traversal
                with tarfile.open(tar_path, "r:gz") as tar:
                    for member in tar.getmembers():
                        if member.name.endswith("/sing-box"):
                            # Sanitize: force extraction to bin_dir/binary_name
                            member.name = binary_name
                            # Python 3.12+ supports filter='data' for safe extraction
                            try:
                                tar.extract(member, self.bin_dir, filter="data")
                            except TypeError:
                                # fallback for older Python without filter arg
                                tar.extract(member, self.bin_dir)
                            break
                    else:
                        logger.error("sing-box binary not found in archive")
                        return False

                if os.path.exists(target_path):
                    os.chmod(target_path, 0o755)
                    os.remove(tar_path)
                    logger.info(f"sing-box ({binary_name}) installed successfully.")
                    return True
                else:
                    logger.error(f"Failed to extract {binary_name} from archive.")
                    if os.path.exists(self.bin_dir):
                        logger.debug(f"Bin dir contents: {os.listdir(self.bin_dir)}")

            except requests.exceptions.RequestException as e:
                logger.warning(f"Network error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
            except Exception as e:
                logger.warning(f"Error (attempt {attempt + 1}): {e}", exc_info=True)
                if attempt < max_retries - 1:
                    time.sleep(2)

        logger.error("All download attempts failed.")
        if os.path.exists(self.bin_dir):
            logger.debug(f"Bin dir contents: {os.listdir(self.bin_dir)}")
        else:
            logger.debug("Bin directory does not exist")

        return False
