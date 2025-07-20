def validate_node(node: dict, node_specs: dict) -> list:
    node_type = node.get("type")
    spec = node_specs.get(node_type, {})
    required = spec.get("required", [])
    missing = [field for field in required if field not in node.get("parameters", {})]
    return missing
