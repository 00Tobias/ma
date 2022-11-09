import re
import operator as op
import functools

### Parse Input

def parse(form):
    # Match parenthesis and non-alpha-numeric tokens,
    # then treat substrings with '"' as literal strings,
    # and lastly match every other alphanumeric token.
    tokens = re.findall(r'[\(\)\+]|\"(?:[^\"\\]|\\[\s\S])*\"|\w+', form)

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
            token = tokens[index]  # TODO: Catch unbalanced parenthesis here
        return result, index
    return req(1)[0]

### Symbols table
# TODO: Some stuff here does not work

# fmt: off
symbols = {
    "+": "sum(args)",                           # Calculate the sum of the arguments
    "-": "functools.reduce(op.sub, args)",      # Subract every value in a list
    "*": "functools.reduce(op.mul, args, 1)",   # Multiply every value in a list
    "def": "symbols[args[0]] = args[1:]",       # Assign a name to something
    "fn": "lambda fnArgs[:] : args[1:]",        # Function definition
    "py": "exec(args[0])",                      # Evaluates a string as python code
    "print": "print(args[0])"                   # Prints the arguments
}

### Evaluate

def evaluate(form):
    """Compiles lisp code into Python and evaluates it"""
    # This function reversely walks through the tree of s-expressions and 
    # replaces the deepest expression with the return value of the function, 
    # until it reaches the top of the tree.

    def parse_arguments(expression):
        # The first symbol is the function of the s-expression
        # The rest are the arguments
        # if expression[0] == 'fn':
        #     function = expression[0]
        #     # fnArgs = expression[1]
        #     args = expression[1:]
        # else:
        function = expression[0]
        args = expression[1:]
        # If the the arguments contain a known symbol, replace it
        args = [symbols[i] if i in symbols else i for i in args]
        return function, args

    while any(isinstance(i, list) for i in form):
        # First we build a list to keep a record of the indexes of the nested expressions
        expression = form
        expressionPath = []
        while any(isinstance(i, list) for i in expression):
            # Save the parent expression to check the index of the expression inside it
            parentExpression = expression
            # Saves the current root expression to expression
            expression = [i for i in expression if isinstance(i, list)][0]
            # Append the index of current root expression to the path record
            expressionPath.append(parentExpression.index(expression))

        function, args = parse_arguments(expression)

        # Lastly we use the values we've gathered to replace the deepest expression with it's return value
        replace_nested_expression(
            form,
            expressionPath,
            eval(symbols[function])
        )
        # ... And loop over again

    # After the form no longer has any nested expressions, we can simply return the return value of the form
    expression = form
    function, args = parse_arguments(expression)

    return exec(symbols[function])


def replace_nested_expression(expression, expressionPath, returnValue):
    """Replaces the deepest expression from a path index with the functions return value"""
    for i in expressionPath[:-1]:
        expression = expression[i]
    lastIndex = expressionPath[-1]
    expression[lastIndex] = returnValue

# Step 4
# Print results and loop (TODO: User input)

### REPL
# Examples: (print "Hello, world!")
#           (print (+ 1 (+ 2 (+ 3 3) (+ 4 4))))
#           (print (py "1 + 1"))
#           (py "print('Hello from Python!')")
#           (def x (+ 1 1))
#           (print x)
#           (py "print(symbols['x'])")

def repl():
    expression = input("> ")
    try:
        print(evaluate(parse(expression)))
        repl()
    except:
        repl()
repl()