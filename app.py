from regex_normalizer.normalizer import normalize_regex


def main():
    print("Hello World!")
    
if __name__ == '__main__':
    regex = r"(\.|\*)+([A-Za-z])[0-9]"
    tokens = normalize_regex(regex)
    print("Tokens normalizados:", tokens)