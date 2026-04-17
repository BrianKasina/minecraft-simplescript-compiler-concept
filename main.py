from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.errors import CompilerError
from compiler.tacGenerator import TACGenerator

def compile_minecraft_script(source_code):
    #remove white spaces from the source code so that the error handling with numbering will properly reflect the user
    #code view

    source_code = source_code.strip()
    try:
        lexer = Lexer()
        tokens = lexer.tokenize(source_code)
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        tac_gen = TACGenerator()
        tac = tac_gen.generate(ast)
        
        print("⛏️ Compilation Successful! TAC:")
        print('\n'.join(tac))
    
    except CompilerError as e:
        print(f"💥 {e}")

#to test error handling i will create a statement that does not adhere to the syntax of the language
# this will raise a syntax error, which will be caught by the try except block in the compile_minecraft_script function
if __name__ == "__main__":
    code = """
    
    craft power = ;
    mine (power > 64) {
        craft enchantment = "Efficiency V!";
    }
    """
    compile_minecraft_script(code)