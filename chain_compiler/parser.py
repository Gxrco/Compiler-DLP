from chain_compiler.tools.shunting_yard import convert_to_postfix

def parse_tokens(tokens):
    postfix_tokens = convert_to_postfix(tokens)
    return postfix_tokens


