def check_emil(value):
    if " "  in value:
        return False

    if len(value) <= 6:
        return False

    if "@" not in value:
        return False

    return True