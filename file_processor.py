
def read_regex_from_file(file_path):
    """
    Reads regex patterns from a file.
    Each line in the file is treated as a separate regex pattern.
    
    Args:
        file_path (str): Path to the file containing regex patterns
        
    Returns:
        list: List of regex patterns
    """
    try:
        with open(file_path, 'r') as file:
            # Read lines and strip whitespace
            regex_patterns = [line.strip() for line in file if line.strip()]
        return regex_patterns
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []
