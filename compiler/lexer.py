import re
from compiler.errors import LexError

class Lexer:
    def __init__(self):
        ...
        #this is the  lexer class responsible for tokenizing the source code before it is passed to the parser
        #it uses regular expressions defined in the token specs list, in order to identify different types of tokens
        #that are acceptible according to the minecraft oriented language syntax which i have chosen for my simplescript compiler
        #the lexer will also remove comments and whitespace from the source code, and will raise an error if it encounters an unexpected token
        #by using the imported LexError class, imported from the errors class, responsible for displaying errors to the users
        #as the compiler handled error handling as well.
        ...
        self.token_specs = [
            ('CRAFT', r'\bcraft\b'), #This is used to declare variables in the language
            ('MINE', r'\bmine\b'), # this is used to start a block of conditional, like the way an if statement would in any other language
            ('ELSE_BLOCK', r'\belse_block\b'),#this is used to represent the else statement in the language that would come after the craft keyword
            ('DIG', r'\bdig\b'), # this is used to start a loop, like the way a while statement would in any other language
            ('ENCHANT', r'\benchant\b'), #this is used to delcare functions in context of the game
            ('DIAMOND', r'\bdiamond\b'), # this is used to represent the booleant value for true
            ('COBBLESTONE', r'\bcobblestone\b'), # this is used to represent the boolean value for false, since diamond is more valuable
            ('IDENTIFIER', r'[a-zA-Z_]\w*'), # 
            ('LITERAL', r'\d+(\.\d+)?|"[^"]*"'), 
            ('OPERATOR', r'[+\-*/]|==|!=|<|>|='),
            ('DELIMITER', r'[();{},]'),
            ('SKIP', r'\s+|//.*|\/\*[\s\S]*?\*\/'), # this defines values like whitespaces that should be skipped by the lexer
        ]
        self.keywords = {'craft', 'mine', 'else_block', 'dig', 'enchant', 'diamond', 'cobblestone'}

    def tokenize(self, code):
        ...
        # the tokenise function  works using the re module which provides support for 
        #regular expressions, tokens is defined, as an empty list to store the tokens created by the function, 
        #the variabled line num and line start are used to keep track of what line of the source code is being tokenised for pusposes of error handling
        #while the regex function uses the named group syntax to create a single regex expression of the language keywords, seperating them using the or
        #operator the P<name>pattern) syntax gives a name to each matching group, allowing the code to identify which token type was matched
        #for match in re.finditer(regex, code):: This loop iterates through all the non-overlapping matches found in the code using the combined regular expression
        #
        ...
        tokens = []
        line_num = 1
        line_start = 0
        regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_specs)
        for match in re.finditer(regex, code):
            kind = match.lastgroup 
            value = match.group() #This gets the actual text that was matched.
            start = match.start() #This gets the starting position of the match in the code.
            line = line_num + code.count('\n', 0, start) # calculates the line number of the token
            
            if kind == 'SKIP': # ensures that any whitespaces, comments etc are not tokenised and are instead skipped
                if '\n' in value:
                    line_num += value.count('\n')
                continue
            elif kind == 'LITERAL' and value.startswith('"'): #If the token is a 'LITERAL' and starts with a double quote (")
                value = value.strip('"')  # Remove quotes
            elif kind == 'IDENTIFIER' and value in self.keywords: 
                #If the token is an 'IDENTIFIER' and its value is present in the self.keywords set, 
                #the kind of the token is changed to the uppercase version of the keyword
                kind = value.upper()  # e.g, 'craft' to 'CRAFT'
            
            # Track line numbers for error reporting, so that proper errors are displayed to the person writing the source code
            tokens.append({
                'kind': kind,
                'value': value,
                'line': line,
                'column': start - code.rfind('\n', 0, start)
            })
        if match and match.end() < len(code):
            # Calculate the line number for the error
            error_pos = match.end()
            error_line = line_num + code.count('\n', 0, error_pos)
            raise LexError(f"Unexpected character '{code[error_pos]}'", 
                        line=error_line, 
                        code_snippet=f"Line {error_line}: {code[error_pos]}")
        return tokens