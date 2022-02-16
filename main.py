sep = ","
layout = [
    sep.join(" q w e r t y u i o p ").split(sep),
    sep.join(" a s d f g h j k l ' ").split(sep),
    sep.join("    z x c v b n m    ").split(sep)
]

ROWS = 3
COLS = 21

indexes = {}

def sort_keys_by_val(dic):
    return sorted(dic, key=lambda x: dic[x], reverse=True)

def calculate_indexes():
    for row in range(ROWS):
        for col in range(COLS):
            button = layout[row][col]
            if button != ' ':
                indexes[button] = (row, col)

def find_neighbors_of(letter):
    row, col = indexes[letter]

    m = [[], [], []]

    for r in range(3):
        cur_row = row-(1-r)
        if -1 < cur_row < ROWS:
            for c in range(col-2, col+3):
                if -1 < c < COLS:
                    m[r].append(layout[cur_row][c])
                else:
                    m[r].append(None)
        else:
            m[r] = [None for _ in range(5)]

    return m

def give_weights(neighbors):
    w = {}

    for r in range(3):
        if any(neighbors[r]):
            row = neighbors[r]

            if r == 1: # middle
                for c in [0, 4]:
                    if row[c]:
                        w[row[c]] = 0.1

            else: # top and bottom
                for c in range(5):
                    dist = 0.05/(abs(2-c)+1)
                    if row[c]:
                        w[row[c]] = round(dist, 3)
    w.pop(' ')
    return w

def generate_rule(letter, weights):
    upper = "Sq" if letter == "'" else letter.upper()
    wkeys = sort_keys_by_val(weights)

    rule = [f"define Noise{upper} [ {letter} (->) {wkeys[0]}::{weights[wkeys[0]]} ] .o."]
    indent = ' ' * len(rule[0].split("[")[0])

    for w in wkeys[1:]:
        rule.append(f"{indent}[ {letter} (->) {w}::{weights[w]} ] .o.")
    
    rule[-1] = ";".join(rule[-1].rsplit(".o.", 1))
    return '\n'.join(rule)

def generate_xfst(rules):
    combined_rule = ["define NoiseModel NoiseA |"]
    indent = " " * 18

    abc = [chr(_) for _ in range(66, 91)]
    for i in abc:
        combined_rule.append(f"{indent}Noise{i} |")
    
    combined_rule.append(f"{indent}NoiseSq ;")
    combined_rule =  "\n".join(combined_rule)

    setup = "\n".join([
        "regex NoiseModel;",
        "invert net",
        "set print-weight ON",
        "save stack kb_noise.hfst",
        "clear"
    ])

    rules.append(combined_rule)
    rules.append(setup)
    
    return "\n\n".join(rules)


if __name__ == '__main__':
    calculate_indexes()

    filename = "kb_noise.xfst"
    
    letters = [chr(_) for _ in range(97, 123)] + ["'"]
    rules = []
    for letter in letters:
        neighbors = find_neighbors_of(letter)
        weights = give_weights(neighbors)
        rules.append(generate_rule(letter, weights))
    
    with open(filename, mode="w", encoding="utf-8") as f:
        f.write(generate_xfst(rules))
    
