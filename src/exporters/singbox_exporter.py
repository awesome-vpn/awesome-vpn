"""Sing-box JSON exporter."""

import json


class SingboxExporter:
    @staticmethod
    def export(nodes, filepath):
        """Export nodes to sing-box format."""
        # Remove internal fields
        clean_nodes = []
        for node in nodes:
            clean = {k: v for k, v in node.items() if not k.startswith('_')}
            clean_nodes.append(clean)
        
        with open(filepath, 'w') as f:
            json.dump({"outbounds": clean_nodes}, f, indent=2, ensure_ascii=False)
        
        return filepath
