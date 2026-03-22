import os
import tarfile
import platform
import requests
import time
import re

class BinaryManager:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.bin_dir = os.path.join(self.base_dir, 'bin')
        self.sing_box_path = None

    def get_singbox_path(self):
        print(f"Current working directory: {os.getcwd()}")
        print(f"Bin directory: {self.bin_dir}")
        
        if not os.path.exists(self.bin_dir):
            print(f"Creating bin directory: {self.bin_dir}")
            try:
                os.makedirs(self.bin_dir, exist_ok=True)
                print(f"Successfully created bin directory")
            except Exception as e:
                print(f"Failed to create bin directory: {e}")
                return None
            
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        print(f"System: {system}, Machine: {machine}")
        
        if machine == 'x86_64':
            machine = 'amd64'
        elif machine == 'aarch64':
            machine = 'arm64'
            
        binary_name = f"sing-box-{system}-{machine}"
        sing_box_path = os.path.join(self.bin_dir, binary_name)
        
        print(f"Looking for sing-box at: {sing_box_path}")
        
        if os.path.exists(sing_box_path):
            print(f"Using existing sing-box binary: {sing_box_path}")
            self.sing_box_path = sing_box_path
            return sing_box_path
        
        print(f"sing-box binary ({binary_name}) not found. Attempting to download...")
        
        version = self._get_latest_version()
        if not version:
            version = "1.10.7"
            print(f"Could not fetch latest version, using fallback: {version}")
        else:
            print(f"Latest sing-box version: {version}")
        
        url = self._get_download_url(version, system, machine)
        
        if url:
            print(f"Download URL: {url}")
            success = self._download_with_retry(url, sing_box_path, binary_name)
            if success:
                self.sing_box_path = sing_box_path
                return sing_box_path
        
        print(f"Auto-download failed. Please install sing-box manually to 'bin/{binary_name}'")
        return None

    def _get_latest_version(self):
        # Check for pinned version in environment
        pinned = os.getenv('SING_BOX_VERSION')
        if pinned:
            return pinned.lstrip('v')
        try:
            api_url = "https://api.github.com/repos/SagerNet/sing-box/releases/latest"
            headers = {"Accept": "application/vnd.github.v3+json"}
            resp = requests.get(api_url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                tag_name = data.get('tag_name', '')
                if tag_name.startswith('v'):
                    return tag_name[1:]
                return tag_name
        except Exception as e:
            print(f"Failed to fetch latest version: {e}")
        return None

    def _get_download_url(self, version, system, machine):
        base_url = f"https://github.com/SagerNet/sing-box/releases/download/v{version}"
        
        if system == 'darwin':
            if machine == 'arm64':
                return f"{base_url}/sing-box-{version}-darwin-arm64.tar.gz"
            else:
                return f"{base_url}/sing-box-{version}-darwin-amd64.tar.gz"
        elif system == 'linux':
            if machine == 'amd64':
                return f"{base_url}/sing-box-{version}-linux-amd64.tar.gz"
            elif machine == 'arm64':
                return f"{base_url}/sing-box-{version}-linux-arm64.tar.gz"
        
        return None

    def _download_with_retry(self, url, target_path, binary_name, max_retries=3):
        for attempt in range(max_retries):
            try:
                print(f"Downloading sing-box (attempt {attempt + 1}/{max_retries})...")
                print(f"URL: {url}")
                print(f"Target path: {target_path}")
                
                # Test network connectivity first
                print("Testing network connectivity...")
                test_resp = requests.get("https://github.com", timeout=10)
                print(f"GitHub connectivity test: HTTP {test_resp.status_code}")
                
                resp = requests.get(url, stream=True, timeout=120)
                print(f"Download response status: {resp.status_code}")
                print(f"Download headers: {dict(resp.headers)}")
                
                if resp.status_code != 200:
                    print(f"Download failed: HTTP {resp.status_code}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    return False
                
                tar_path = os.path.join(self.bin_dir, f'{binary_name}.tar.gz')
                print(f"Saving tar to: {tar_path}")
                total_size = int(resp.headers.get('content-length', 0))
                print(f"Expected file size: {total_size} bytes")
                downloaded = 0
                
                with open(tar_path, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rDownloading: {percent:.1f}%", end='', flush=True)
                
                print("\nDownload complete. Verifying tar file...")
                if not os.path.exists(tar_path):
                    print(f"Tar file not created: {tar_path}")
                    return False
                
                tar_size = os.path.getsize(tar_path)
                print(f"Tar file size: {tar_size} bytes")
                
                print("Extracting...")
                with tarfile.open(tar_path, 'r:gz') as tar:
                    print("Listing archive contents:")
                    for member in tar.getmembers():
                        print(f"  - {member.name}")
                        if member.name.endswith('/sing-box'):
                            member.name = binary_name
                            print(f"  Extracting to: {os.path.join(self.bin_dir, binary_name)}")
                            tar.extract(member, self.bin_dir)
                            break
                
                if os.path.exists(target_path):
                    file_size = os.path.getsize(target_path)
                    print(f"Extracted file size: {file_size} bytes")
                    os.chmod(target_path, 0o755)
                    print(f"Set executable permission: 0o755")
                    os.remove(tar_path)
                    print(f"Removed tar file: {tar_path}")
                    print(f"sing-box ({binary_name}) installed successfully.")
                    return True
                else:
                    print(f"Failed to extract {binary_name} from archive.")
                    print(f"Checking bin directory contents:")
                    for item in os.listdir(self.bin_dir):
                        print(f"  - {item}")
                    
            except requests.exceptions.RequestException as e:
                print(f"\nNetwork error: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
            except Exception as e:
                print(f"\nError: {e}")
                import traceback
                traceback.print_exc()
                if attempt < max_retries - 1:
                    time.sleep(2)
        
        print(f"All download attempts failed. Checking bin directory:")
        if os.path.exists(self.bin_dir):
            for item in os.listdir(self.bin_dir):
                print(f"  - {item}")
        else:
            print("  Bin directory does not exist")
        
        return False
