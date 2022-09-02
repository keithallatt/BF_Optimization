import time
from typing import List

# CONSTANTS FIRST
INFINITE_TAPE = False
TAPE_LENGTH = 24
CYCLIC_TAPE = True


class BFTape:
    def __init__(self):
        self.pointer_index = 0
        self.tape_contents = dict()
        self.input_feed = []
        self.output_feed = []

    def debug_set_contents(self, contents: dict):
        self.tape_contents = {k: v % 256 for k, v in contents.items() if v % 256}

    def peek(self):
        return self.tape_contents.get(self.pointer_index, 0)

    def pointer(self, c):
        self.pointer_index += c
        if 0 <= self.pointer_index < TAPE_LENGTH:
            return
        if not INFINITE_TAPE:
            if not CYCLIC_TAPE:
                raise IndexError(f"Pointer index out of range: {self.pointer_index}")
            self.pointer_index %= TAPE_LENGTH

    def modify(self, c):
        value = 0
        if self.pointer_index in self.tape_contents.keys():
            value = self.tape_contents.pop(self.pointer_index)
        value += c
        value %= 256
        if value:
            self.tape_contents[self.pointer_index] = value

    def get_input(self):
        while not self.input_feed:
            _in = input('> ')
            self.input_feed += list(map(ord, _in))
        self.tape_contents[self.pointer_index] = self.input_feed.pop(0)
        if not self.tape_contents[self.pointer_index]:
            self.tape_contents.pop(self.pointer_index)

    def output(self, c):
        self.output_feed += [chr(self.tape_contents.get(self.pointer_index, 0))] * c

    def __str__(self):
        return str(self.tape_contents)


class BFTokenizer:
    """ tokenizes into easily processable tokens """
    def __init__(self):
        self.tokens = []
        self.instructions = []

    def parse_code(self, code):
        code = ''.join(filter(lambda x: x  in '[]<>+-.,',  code))

        def split(c: str, ind_err: int):
            # split into 'beginning (with no [])' / '[' / 'middle (with matching [])' / ']' / 'end (with matching [])'
            if '[' not in c:
                if ']' in c:
                    e_ind = ind_err + c.index(']')
                    e_str = f'Mismatched brackets: ] at index {e_ind}\n{c}\n'
                    e_str += ("_" * (c.index(']'))) + "^"

                    raise SyntaxError(e_str)

                return [c] if c else []

            # [ in code

            i1 = c.index('[')
            beginning = c[:i1]

            if ']' in beginning:
                e_ind = ind_err + c.index(']')
                e_str = f'Mismatched brackets: ] at index {e_ind}\n{c}\n'
                e_str += ("_" * (c.index(']'))) + "^"

                raise SyntaxError(e_str)

            if ']' not in c:
                raise SyntaxError('Missing ]')

            i2 = c.index(']', i1)

            while c.count('[', i1, i2+1) != c.count(']', i1, i2+1):
                try:
                    i2 = c.index(']', i2+1)
                except ValueError:
                    raise SyntaxError("Missing ]")
            middle = split(c[i1+1:i2], i1+1)
            end = split(c[i2+1:], i2+1)

            return [beginning, middle] + end

        self.tokens = split(code, 0)

    def build_functions(self):
        self.instructions = self._build_functions()

    def _build_functions(self, code_snippet=None):
        if code_snippet is None:
            code_snippet = self.tokens

        if isinstance(code_snippet, list):
            return list(map(self._build_functions, code_snippet))

        assert set(code_snippet).issubset(set('+-,.<>'))

        if not code_snippet:
            def no_op(*args, **kwargs):
                pass

            return no_op

        # first turn into (char, int) pairs that correspond to
        # the number of consecutive occurrences of that character
        occs, code_snippet = [(code_snippet[0], 1)], code_snippet[1:]

        while code_snippet:
            c1, o = occs.pop(-1)
            c2, code_snippet = code_snippet[0], code_snippet[1:]
            if c1 == c2:
                occs.append((c1, o+1))
            else:
                occs.append((c1, o))
                occs.append((c2, 1))

        def occ2inst(co):
            c, o = co
            return {
                '+': lambda tape: BFTape.modify(tape, o),
                '-': lambda tape: BFTape.modify(tape, -o),
                '<': lambda tape: BFTape.pointer(tape, -o),
                '>': lambda tape: BFTape.pointer(tape, o),
                ',': lambda tape: BFTape.get_input(tape),
                '.': lambda tape: BFTape.output(tape, o)
            }.get(c, lambda tape: lambda: None)

        insts = list(map(occ2inst, occs))

        def wrapper(tape: BFTape):
            for instruction in insts:
                instruction(tape)

        return wrapper

    def run(self, tape: BFTape, timeout=None, framerate=None):
        t1 = time.time()

        def run_list(lst):
            for instruction in lst:
                if isinstance(instruction, list):
                    while tape.peek():
                        run_list(instruction)
                else:
                    instruction(tape)
                    if framerate and framerate > 0:
                        t_str = [str(tape.tape_contents.get(i, 0)).rjust(3) for i in range(TAPE_LENGTH)]
                        t_str[tape.pointer_index] = f"*{t_str[tape.pointer_index]}*"


                        print("\r"+" | ".join(t_str), end="")
                        time.sleep(1.0 / framerate)

            if timeout is not None and time.time() - t1 > timeout:
                raise TimeoutError()

        run_list(self.instructions)


def run_bf(code: str, contents: dict = None, pre_compiled: BFTokenizer = None,
           input_feed: List[int] = None, timeout: int = None, framerate: int = None):
    bf_tape = BFTape()
    if input_feed is not None:
        bf_tape.input_feed = input_feed
    if contents is not None:
        bf_tape.debug_set_contents(contents)

    if pre_compiled is not None:
        bf_token = pre_compiled
    else:
        bf_token = BFTokenizer()
        bf_token.parse_code(code)
        bf_token.build_functions()

    bf_token.run(bf_tape, timeout=timeout, framerate=framerate)
    return bf_tape
