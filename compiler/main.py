from tokenizer import Tokenizer

if __name__ == '__main__':
    tokens = Tokenizer.tokenize("5+6;", "test")
    for token in tokens:
        print(token)
