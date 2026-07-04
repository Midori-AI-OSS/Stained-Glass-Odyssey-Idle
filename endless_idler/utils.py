def normalize_progress(value: float, max_val: float) -> float:
    """Convert arbitrary value/max to 0.0-1.0 normalized range"""
    return 0.0 if max_val <= 0 else min(1.0, max(0.0, value / max_val))
