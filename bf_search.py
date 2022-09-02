import functools
import json
import os.path
import pprint
from typing import List

from bf_interpreter import run_bf
import tqdm


@functools.lru_cache(maxsize=3)
def get_ints():
    # general format
    # regex_pattern = re.compile(r"^(\++|-+)(\[>(\++|-+)<-\]>(\++|-+))?$")

    total = 0

    ints = {}

    while True:
        to_consider = []
        for b in range(total+1):
            for cb in "+-":
                bs = cb * b
                tp = run_bf(bs)
                vp = tp.peek()
                to_consider.append((bs, vp))

                for m in range(1, total+1 - b):
                    e = total - b - m

                    for cm in "+-":
                        ms = cm * m

                        for em in "+-":
                            es = em * e

                            s = f">{bs}[<{ms}>-]<{es}"
                            t = run_bf(s)
                            v = t.peek()
                            to_consider.append((s, v))

                for string, value in to_consider:
                    if value in ints.keys():
                        old_str = ints[value]
                        if len(string) < len(old_str):
                            ints[value] = string
                    else:
                        ints[value] = string
        total += 1
        if len(ints.keys()) == 256:
            break

    return ints


def write_buffer(buffer_data: List[int], clean=False, output=False):
    output_str = list(map(lambda x: f"{'' if clean else '[-]'}{INTS[x%256]}{'.' if output else ''}>", buffer_data))
    output_str = "".join(output_str)[:-1].replace("<>", '')
    return output_str


if __name__ == '__main__':
    if not os.path.exists("ints_bf.json"):
        INTS = get_ints()
        with open("ints_bf.json", 'w') as f:
            json.dump(INTS, f, indent=2, sort_keys=True)
    else:
        with open("ints_bf.json", 'r') as f:
            INTS = {int(k): v for k, v in json.load(f).items()}

