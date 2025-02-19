import os.path


def read_csv(file_path: str) -> list[dict]:
    result: list[dict] = []
    keys: list[str] = []

    def parse_single_value(t: str) -> str | int | float:
        try:
            return int(t)
        except ValueError:
            pass

        try:
            return float(t)
        except ValueError:
            pass

        return t


    def parse_line(l: str) -> dict:
        has_open_quotation_marks: bool = False
        res: dict = {}
        index: int = 0
        elem: str = ""

        for c in l: # stream through the line character by character
            if c == '"':
                has_open_quotation_marks = not has_open_quotation_marks
                continue

            if c == ',':
                if has_open_quotation_marks: # ignore the comma and append it to the result value
                    elem += c
                    continue

                else: # the next value starts
                    parsed = parse_single_value(elem)
                    elem = ''
                    k: str = keys[index]
                    index += 1
                    res[k] = parsed
                    continue

            elem += c

        # add the remaining string to the dict
        parsed = parse_single_value(elem)
        k: str = keys[index]
        res[k] = parsed

        if has_open_quotation_marks:
            raise SyntaxError

        return res

    if not os.path.exists(file_path):
        print("file not exist")
        return []


    with open(file_path, 'r') as f:
        line_count: int = 0

        for line in f:
            line = line.removesuffix('\n') # ignore nl at the end
            if line.isspace():
                continue # ignore empty lines

            # first line_count contains key names
            line_count += 1

            if line_count == 1:
                for key in line.split(","):
                    keys.append(key)
                continue

            # read in te values
            d = parse_line(line)
            result.append(d)

    return result


def write_csv(file_path: str, content: list[dict]) -> None:
    def find_keys() -> list[str]:
        result: list[str] = []
        di: dict = content[0]

        for key in di:
            result.append(str(key))

        del di
        return result


    if len(content) < 1:
        return

    keys: list[str] = find_keys()

    with open(file_path, 'w') as f:
        # write the keys first
        first_key: bool = True
        for k in keys:
            if ',' in k:
                f.write('"') # surround keys containing commas with quotation marks

            if not first_key:
                f.write(',')

            f.write(k)
            if ',' in k:
                f.write('"') # surround keys containing commas with quotation marks

            first_key = False

        f.write('\n')

        # write the values
        for d in content:
            first_value: bool = True

            for k in keys: # assure the values are in the same order with the keys
                value: str = str(d[k])
                if ',' in value:
                    f.write('"') # surround values containing commas with quotation marks

                if not first_value:
                    f.write(',')
                f.write(value)

                if ',' in value:
                    f.write('"') # surround values containing commas with quotation marks

                first_value = False
            f.write('\n')
