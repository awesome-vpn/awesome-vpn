import os
import json
import subprocess
import time
import tempfile
import concurrent.futures
import random
import sys
import logging
import requests
import platform
import shutil

TEST_URLS = [
    'http://www.google.com/generate_204',
]

class Validator:
    def __init__(self, sing_box_path=None):
        if sing_box_path and os.path.exists(sing_box_path):
            self.sing_box_path = sing_box_path
        else:
            self.sing_box_path = self._find_sing_box()
        
        if self.sing_box_path and os.path.exists(self.sing_box_path):
            print(f"Validator: Using sing-box at {self.sing_box_path}")
        else:
            print(f"Validator: sing-box binary not found. Validation will be skipped.")
        
        self.logger = logging.getLogger('Validator')

    def _find_sing_box(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bin_dir = os.path.join(base_dir, 'bin')
        
        system = platform.system().lower()
        machine = platform.machine().lower()
        if machine == 'x86_64':
            machine = 'amd64'
        elif machine == 'aarch64':
            machine = 'arm64'
        
        possible_names = [
            f"sing-box-{system}-{machine}",
            "sing-box",
            f"sing-box-{system}-amd64",
            f"sing-box-{system}-arm64",
        ]
        
        for name in possible_names:
            path = os.path.join(bin_dir, name)
            if os.path.exists(path):
                return path
        
        global_path = shutil.which('sing-box')
        if global_path:
            return global_path
        
        return None

    def tcp_ping(self, host, port, timeout=3):
        import socket
        try:
            with socket.create_connection((host, int(port)), timeout=timeout):
                return True
        except:
            return False

    def validate_nodes_parallel(self, nodes, timeout=5, max_workers=5):
        """
        Validate multiple nodes in parallel
        """
        if not self.sing_box_path or not os.path.exists(self.sing_box_path):
            print(f"Warning: sing-box not available, skipping validation. All {len(nodes)} nodes will be kept.")
            return nodes
        
        valid_nodes = []
        print(f"Starting parallel validation for {len(nodes)} nodes with {max_workers} threads...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_node = {executor.submit(self.validate_node, node, timeout): node for node in nodes}
            for i, future in enumerate(concurrent.futures.as_completed(future_to_node)):
                node = future_to_node[future]
                try:
                    if future.result():
                        valid_nodes.append(node)
                except Exception as exc:
                    pass
                if (i + 1) % 50 == 0:
                    print(f"Validated {i + 1}/{len(nodes)} nodes, {len(valid_nodes)} valid so far...")
        return valid_nodes

    def validate_node(self, node, timeout=5):
        """
        Validate a single node by starting sing-box and testing through it.
        The test verifies that the proxy connection works, regardless of direct connectivity.
        """
        if not self.sing_box_path or not os.path.exists(self.sing_box_path):
            return True

        server = node.get('server')
        port = node.get('server_port') or node.get('port')
        if server and port:
            if not self.tcp_ping(server, port, timeout=3):
                return False

        node_config = node.copy()
        keys_to_remove = [k for k in list(node_config.keys()) if k.startswith('_')]
        for k in keys_to_remove:
            del node_config[k]
        
        if "tag" not in node_config:
            node_config["tag"] = "proxy"

        listen_port = random.randint(10000, 60000)
        
        test_config = {
            "log": {
                "level": "fatal",
                "timestamp": True
            },
            "inbounds": [
                {
                    "type": "socks",
                    "tag": "socks-in",
                    "listen": "127.0.0.1",
                    "listen_port": listen_port
                }
            ],
            "outbounds": [
                node_config,
                {
                    "type": "direct",
                    "tag": "direct"
                }
            ],
            "route": {
                "rules": [
                    {
                        "inbound": "socks-in",
                        "outbound": node_config.get("tag", "proxy")
                    }
                ]
            }
        }
        
        proc = None
        tmp_config_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
                json.dump(test_config, tmp_file)
                tmp_config_path = tmp_file.name
            
            cmd = [self.sing_box_path, 'run', '-c', tmp_config_path]
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
            
            time.sleep(1)
            
            if proc.poll() is not None:
                return False
                
            proxies = {
                'http': f'socks5://127.0.0.1:{listen_port}',
                'https': f'socks5://127.0.0.1:{listen_port}'
            }
            
            success = False
            
            for target_url in TEST_URLS:
                try:
                    resp = requests.get(target_url, proxies=proxies, timeout=timeout)
                    if resp.status_code == 204:
                        success = True
                        break
                except:
                    pass
            
            return success
                
        except Exception as e:
            return False
        finally:
            if proc:
                try:
                    proc.terminate()
                    proc.wait(timeout=1)
                except:
                    proc.kill()
            
            if tmp_config_path and os.path.exists(tmp_config_path):
                try:
                    os.remove(tmp_config_path)
                except:
                    pass
