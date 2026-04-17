class CompilerError(Exception):
    def __init__(self, message, line=None, code_snippet=""):
        # This is the base CompilerError class that all specific error types inherit from
        # It provides a consistent way to format and display errors in our Minecraft-themed compiler
        # The error message includes a pickaxe emoji (⛏️) to keep everything consistent with the Minecraft theme
        # The compile error class inherits from the base exception class of python and then allows all the different 
        # types of errors to inherit from this base class, ensuring they propagate from the  different classes and are 
        # presented upon an exception occuring. the main.py is then wrapped in a try except block, to ensure that any errors
        # which occur during the program lifecylce are properly captured and displayed.
        
        
        self.message = f"⛏️ Error (Line {line}): {message}\n  {code_snippet.strip()}"

        super().__init__(self.message)

class SyntaxError(CompilerError):
    # SyntaxError is raised when the parser encounters invalid syntax
    # For example, missing semicolons, mismatched parentheses, or invalid statement structure
    pass

class LexError(CompilerError):
    # LexError is raised when the lexer encounters invalid tokens
    # For example, invalid characters or malformed string literals
    pass

class SemanticError(CompilerError):
    # SemanticError is raised when there's a problem with the meaning of the code
    # For example, using undeclared variables or type mismatches
    pass