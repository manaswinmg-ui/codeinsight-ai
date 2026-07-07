from app.repository.file_descriptor import FileDescriptor


class TreeBuilder:
    @staticmethod
    def build_tree_dict(descriptors: list[FileDescriptor]) -> dict:
        """
        Builds a nested dictionary representation of the directory structure.
        """
        tree = {}
        for d in descriptors:
            parts = d.relative_path.replace("\\", "/").split("/")
            current = tree
            for part in parts:
                if not part:
                    continue
                if part not in current:
                    current[part] = {}
                current = current[part]
        return tree

    @classmethod
    def render_ascii(cls, tree: dict, prefix: str = "") -> str:
        """
        Recursively renders a nested dictionary directory tree into an ASCII string.
        """
        lines = []
        keys = sorted(tree.keys())
        for idx, key in enumerate(keys):
            is_last = (idx == len(keys) - 1)
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{key}")
            
            sub_tree = tree[key]
            if sub_tree:
                extension_prefix = "    " if is_last else "│   "
                sub_render = cls.render_ascii(sub_tree, prefix + extension_prefix)
                if sub_render:
                    lines.append(sub_render)
        return "\n".join(lines)
