from chain_compiler.tools.regex_parser import tokenize


def normalize_regex(regex):
    tokens = tokenize(regex)
    return tokens

