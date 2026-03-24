"""Base64 subscription exporter."""

import base64


class Base64Exporter:
    @staticmethod
    def export(nodes, link_map, filepath):
        """Export nodes to base64-encoded proxy links."""
        links = []
        for node in nodes:
            tag = node.get('tag', '')
            original_link = link_map.get(tag, '')
            
            if original_link:
                links.append(original_link)
            else:
                server = node.get('server', '')
                port = node.get('server_port') or node.get('port', '')
                ntype = node.get('type', '')
                links.append(f"{ntype}://{tag}@{server}:{port}")
        
        raw = '\n'.join(links)
        encoded = base64.b64encode(raw.encode()).decode()
        
        with open(filepath, 'w') as f:
            f.write(encoded)
        
        return filepath
