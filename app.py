from chain_compiler.normalizer import normalize_regex
from chain_compiler.tools.shunting_yard import convert_to_postfix

def main():
    print("Hello World!")
    
if __name__ == '__main__':
    regex = r"(\W|^)[\w.\-]{0,25}@(yahoo|hotmail|gmail)\.com(\W|$)"
    tokens = normalize_regex(regex)
    postfix_tokens = convert_to_postfix(tokens)
    print("Tokens en notación postfix:", postfix_tokens)