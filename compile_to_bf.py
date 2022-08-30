import dataclasses
import json
import pprint

from bf_interpreter import run_bf


@dataclasses.dataclass
class CodeSnippet:
    description: str = "--"
    code: str = ""


with open("ints_bf.json", 'r') as f:
    INTS = {int(k): CodeSnippet(description=f"Set number {k}", code=v) for k, v in json.load(f).items()}


class CodeBuilder:
    def __init__(self):
        self.code_snippets = []

    def clear_cell(self):
        self.code_snippets.append(CodeSnippet("Clear Cell", "[-]"))

    def set_value(self, value):
        self.code_snippets.append(INTS[value])

    def move_pointer(self, offset):
        self.code_snippets.append(CodeSnippet(f"Move {abs(offset)} cells {'right' if offset > 0 else 'left'}.",
                                              (">" if offset > 0 else "<") * abs(offset)))

    def __str__(self):
        return "\n".join([
            pprint.pformat(self.code_snippets, indent=2),
            self.compile()
            ])

    def compile(self):
        code = ''.join([cs.code for cs in self.code_snippets])

        nullops = {
            "+-", "-+",
            "<>", "><",
            "[]"
        }

        while any([nop in code for nop in nullops]):
            for nullop in nullops:
                code = code.replace(nullop, "")

        # if loop starts at an invariant 0 cell, that loop will *never* run.
        while "][" in code:
            inv_loop = code.index("][") + 1

            nested_counter = 0
            inv_end = -1
            for i, c in enumerate(code[inv_loop:]):
                if c == "[":
                    nested_counter += 1
                elif c == "]":
                    nested_counter -= 1

                if nested_counter == 0:
                    inv_end = i + inv_loop + 1
                    break

            code = code[:inv_loop] + code[inv_end:]

        return code


if __name__ == '__main__':
    cb = CodeBuilder()
    cb.move_pointer(1)
    cb.set_value(157)
    cb.move_pointer(1)
    cb.set_value(3)
    print(cb)
    # compiled = cb.compile()
    # tape = run_bf(compiled, framerate=2)
    # print(tape)
