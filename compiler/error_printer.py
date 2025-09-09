from tokenizer import Token


class ErrorPrinter:
    @staticmethod
    def get_source_line(source, line_start, start):
        offset = start
        while offset < len(source) and source[offset] != '\n':
            offset += 1
        return source[line_start:offset]

    @staticmethod
    def print_error(source: str, origin: Token, message: str):
        source_line = ErrorPrinter.get_source_line(source, origin.line_start, origin.loc.start)

        print(f"Error: {message}")
        print(f"--> test.fl:{origin.loc.line}:{origin.loc.col}")
        print("  |")
        print(f"{origin.loc.line} | {source_line}")
        print("  |", end="")
        print(" " * origin.loc.col, end="")
        print("^" * (origin.loc.end - origin.loc.start))
        print("  |")
