"""Programming works: infix to postfix using a stack (shunting-yard)."""
import re

TOKEN_RE = re.compile(r"\s*(\d+\.?\d*|\.\d+|[A-Za-z_]\w*|[-+*/^%()])")
PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2, "^": 3}
RIGHT_ASSOC = {"^"}


def tokenize(expr):
    tokens, pos = [], 0
    expr = expr.strip()
    while pos < len(expr):
        m = TOKEN_RE.match(expr, pos)
        if not m:
            raise ValueError(f'Unexpected character "{expr[pos:].strip()[0]}".')
        tokens.append(m.group(1))
        pos = m.end()
        while pos < len(expr) and expr[pos].isspace():
            pos += 1
    return tokens


def _validate(tokens):
    """Check the token order so bad input gives a clear message."""
    if not tokens:
        raise ValueError("Type an expression first.")
    expect_operand = True
    depth = 0
    for t in tokens:
        if t == "(":
            if not expect_operand:
                raise ValueError('Missing an operator before "(".')
            depth += 1
        elif t == ")":
            if expect_operand:
                raise ValueError('Missing an operand before ")".')
            depth -= 1
            if depth < 0:
                raise ValueError("Parentheses do not match.")
        elif t in PRECEDENCE:
            if expect_operand:
                hint = " (negative numbers are not supported)" if t in "+-" else ""
                raise ValueError(f'Missing an operand before "{t}"{hint}.')
            expect_operand = True
        else:  # operand
            if not expect_operand:
                raise ValueError(f'Missing an operator before "{t}".')
            expect_operand = False
    if depth != 0:
        raise ValueError("Parentheses do not match.")
    if expect_operand:
        raise ValueError("The expression ends with an operator.")


def infix_to_postfix(expr):
    """Return (postfix_tokens, steps). Each step shows the stack and output."""
    tokens = tokenize(expr)
    _validate(tokens)
    stack, output, steps = [], [], []

    def log(token, action):
        steps.append({"token": token, "action": action,
                      "stack": " ".join(stack) or "empty", "output": " ".join(output) or "empty"})

    for t in tokens:
        if t == "(":
            stack.append(t)
            log(t, "Push to stack")
        elif t == ")":
            while stack[-1] != "(":
                output.append(stack.pop())
            stack.pop()
            log(t, "Pop until \"(\", discard both")
        elif t in PRECEDENCE:
            while (stack and stack[-1] != "(" and
                   (PRECEDENCE[stack[-1]] > PRECEDENCE[t] or
                    (PRECEDENCE[stack[-1]] == PRECEDENCE[t] and t not in RIGHT_ASSOC))):
                output.append(stack.pop())
            stack.append(t)
            log(t, "Operator: pop higher or equal priority, then push")
        else:
            output.append(t)
            log(t, "Operand: send to output")
    while stack:
        output.append(stack.pop())
    log("end", "Pop everything left on the stack")
    return output, steps


def evaluate_postfix(postfix):
    """Evaluate if every operand is a number; otherwise return None."""
    try:
        for t in postfix:
            if t not in PRECEDENCE:
                float(t)
    except ValueError:
        return None
    stack = []
    for t in postfix:
        if t in PRECEDENCE:
            b, a = stack.pop(), stack.pop()
            if t == "+":
                r = a + b
            elif t == "-":
                r = a - b
            elif t == "*":
                r = a * b
            elif t in "/%":
                if b == 0:
                    raise ValueError("Division by zero.")
                r = a / b if t == "/" else a % b
            else:
                try:
                    r = a ** b
                except (OverflowError, ZeroDivisionError):
                    raise ValueError("That result is too large to calculate.")
                if isinstance(r, complex):
                    raise ValueError("That power has no real number result.")
            stack.append(r)
        else:
            stack.append(float(t))
    return stack[0]
