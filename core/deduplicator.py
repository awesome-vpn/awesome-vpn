import hashlib
import json


def ensure_unique_tags(nodes):
    """Rename duplicate, non-empty outbound tags in place.

    sing-box requires tags to be unique across outbounds and endpoints. Keep the
    first occurrence unchanged and suffix later occurrences with `` #N``. Tags
    already present in the input are reserved so a generated suffix never
    steals a name from another node.

    Returns the number of renamed nodes.
    """
    reserved_tags = {
        node.get("tag") for node in nodes if isinstance(node.get("tag"), str) and node.get("tag")
    }
    used_tags = set()
    next_suffix = {}
    renamed = 0

    for node in nodes:
        tag = node.get("tag")
        if not isinstance(tag, str) or not tag:
            continue

        if tag not in used_tags:
            used_tags.add(tag)
            next_suffix.setdefault(tag, 2)
            continue

        suffix = next_suffix.get(tag, 2)
        candidate = f"{tag} #{suffix}"
        while candidate in reserved_tags or candidate in used_tags:
            suffix += 1
            candidate = f"{tag} #{suffix}"

        node["tag"] = candidate
        used_tags.add(candidate)
        next_suffix[tag] = suffix + 1
        renamed += 1

    return renamed


class Deduplicator:
    def __init__(self):
        self.seen_hashes = set()
        self.seen_server_ports = set()

    def is_duplicate(self, node):
        """
        Checks if the node is a duplicate based on a complex hash (type, server, port, path/uuid).
        Returns True if duplicate, False otherwise.
        """
        node_hash = self.calculate_hash(node)
        if node_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(node_hash)
        return False

    def is_redundant_server(self, node):
        """
        Checks if the server:port has already been seen.
        Returns True if redundant, False otherwise.
        """
        server = node.get("server")
        port = node.get("server_port") or node.get("port")

        if not server or not port:
            return False

        key = f"{server}:{port}"
        if key in self.seen_server_ports:
            return True
        self.seen_server_ports.add(key)
        return False

    def reset(self):
        self.seen_hashes.clear()
        self.seen_server_ports.clear()

    def calculate_hash(self, data):
        """
        Calculates a hash for the node based on AutoMergePublicNodes logic.
        Uses SHA256 for stability across runs.
        """
        try:
            node_type = data.get("type")
            if not node_type:
                return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

            path = ""
            if node_type == "vmess":
                # transport is nested in 'transport' field in sing-box config usually,
                # but AutoMergePublicNodes assumes a flat structure or specific keys.
                # We need to adapt to sing-box outbound format.
                # Sing-box format: https://sing-box.sagernet.org/configuration/outbound/vmess/

                # Check for transport path
                transport = data.get("transport", {})
                net = transport.get("type", "")
                path = net + ":"

                if net == "ws":
                    path += transport.get("headers", {}).get("Host", "")
                    path += "/" + transport.get("path", "")
                elif net == "http":  # h2
                    path += ",".join(transport.get("host", []))
                    path += "/" + transport.get("path", "")
                elif net == "grpc":
                    path += transport.get("service_name", "")

                # Add UUID for vmess uniqueness
                path += ":" + data.get("uuid", "")

            elif node_type == "shadowsocks":  # sing-box uses 'shadowsocks' not 'ss'
                path = data.get("password", "")
                # SS in sing-box: method, password.
                # If server:port:method:password are same, it's same.

            elif node_type == "trojan":
                path = data.get("password", "") + ":"
                transport = data.get("transport", {})
                net = transport.get("type", "")

                if net == "ws":
                    path += transport.get("headers", {}).get("Host", "")
                    path += "/" + transport.get("path", "")
                elif net == "grpc":
                    path += transport.get("service_name", "")

            elif node_type == "vless":
                path = data.get("uuid", "") + ":"
                transport = data.get("transport", {})
                net = transport.get("type", "")

                if net == "ws":
                    path += transport.get("headers", {}).get("Host", "")
                    path += "/" + transport.get("path", "")
                elif net == "grpc":
                    path += transport.get("service_name", "")

            else:
                # Fallback for other types (hysteria, etc)
                # Use server:port:type as basic key if parsing fails or not implemented
                server = data.get("server", "")
                port = data.get("server_port") or data.get("port", "")
                path = f"{node_type}:{server}:{port}"

            return hashlib.sha256(path.encode()).hexdigest()

        except Exception:
            # Fallback
            return hashlib.sha256(str(data).encode()).hexdigest()
