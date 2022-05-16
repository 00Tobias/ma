# Step 1
# Read input program TODO: Implement REPL

# Step 2
# Parse Input (Adapted from lis.py)


def parse(program):
    return read_from_tokens(tokenize(program))


def tokenize(s):
    "Convert a string into a list of tokens."
    return s.replace('(', ' ( ').replace(')', ' ) ').split()


def read_from_tokens(tokens):
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0)  # pop off ')'
        print("Tokens:", L)
        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)


def atom(token):
    "Numbers become numbers; every other token is a symbol."
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return str(token)

# Step 3
# Evaluate


symbols = {
    "+": "sum(args)",                      # Calculate the sum of the arguments
    "-": "reduce(op.sub, args)",           # Subract every value from a list
    "def": "def",                          # Assign a name to something
    "fn": "def name arguments:\n body\n",  # Function definition
    # Simply evaluates a string as python code
    "py": "eval(args)",
}


def evaluate(form):
    """Compiles lisp code into Python and uses the eval() function to evaluate it"""
    # This single function took me hours to get this terse lmao
    # It simply walks *reverse* through the tree of s-expressions and replaces the deepest expression
    # with the return value of the function, until it reaches the top of the tree
    # As far as I know it is a completely unique way of evaluating lisp
    # It's usually done with a stack, or using some recursion magic (Which I actually do too)
    while any(isinstance(i, list) for i in form):
        # First we build a list to keep a record of the indexes of the nested expressions
        expression = form
        expressionPath = []
        while any(isinstance(i, list) for i in expression):
            # Save the parent expression to check the index of the expression inside it
            parent_expr = expression
            # Saves the current root expression to expr
            expression = [i for i in expression if isinstance(i, list)][0]
            # Append the index of current root expression to the path record
            expressionPath.append(parent_expr.index(expression))

        # The first symbol is the function of the s-expression
        function = expression[0]
        # The rest are the arguments
        args = expression[1:]

        # Lastly we use the values we've gathered to replace the deepest expression with it's return value
        replace_nested_expression(
            form,
            expressionPath,
            eval(symbols[function])
        )
        # ... And loop over again

    # After the form no longer has any nested expressions, we can simply return the return value of the form
    function = form[0]
    args = form[1:]
    return eval(symbols[function])


def replace_nested_expression(expression, expressionPath, returnValue):
    """Replaces the deepest expression from a path index with the functions return value"""
    for i in expressionPath[:-1]:
        expression = expression[i]
    lastIndex = expressionPath[-1]
    expression[lastIndex] = returnValue

# Step 4
# Print results and loop


inputs = ['(+ 1 (+ 2 (+ 3 3) (+ 4 4)))']
# """(py "print('Hello World!')")"""
# input = "(+ 1 (+ 2 (+ 3 3) (+ 4 4)))"
for input in inputs:
    print("Input was: ", input)
    print("Result was:", evaluate(parse(input)))
