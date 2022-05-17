import re

# Step 1
# Read input program TODO: Implement REPL

# Step 2
# Parse Input


def parse(form):
    # Match parenthesis and non-alpha-numeric tokens,
    # then treat substrings with '"' as literal strings,
    # and lastly match every other alphanumeric token.
    tokens = re.findall(r'[\(\)\+]|\"(?:[^\"\\]|\\[\s\S])*\"|\w+', form)
    print("Tokens:", tokens)

    def req(index):
        result = []
        token = tokens[index]
        while token != ")":
            if token == "(":
                subtree, index = req(index + 1)
                result.append(subtree)
            else:
                # If the token is a string, remove the surrounding quotes
                if "\"" in token:
                    token = token[1:-1]
                # If the token is an integer, make it one
                try:
                    token = int(token)
                except ValueError:
                    try:
                        token = float(token)
                    except ValueError:
                        token = str(token)
                result.append(token)
            index += 1
            token = tokens[index]
        return result, index
    return req(1)[0]

# Step 3
# Evaluate


symbols = {
    "+": "sum(args)",                      # Calculate the sum of the arguments
    "-": "reduce(op.sub, args)",           # Subract every value from a list
    "def": "def",                          # Assign a name to something
    "fn": "def name arguments:\n body\n",  # Function definition
    "py": "eval(args[0])",                 # Evaluates a string as python code
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


inputs = ['(+ 1 (+ 2 (+ 3 3) (+ 4 4)))',
          """(py "print('Hello World!')")""",
          """(py "1 + 1")""", ]

for input in inputs:
    print("Input was: ", input)
    print("Result was:", evaluate(parse(input)))
