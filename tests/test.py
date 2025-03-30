import unittest
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.tacGenerator import TACGenerator
from compiler.errors import CompilerError

class TestLexer(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
    
    def test_basic_tokens(self):
        code = "craft x = 10;"
        tokens = self.lexer.tokenize(code)
        
        # Check token count (craft, x, =, 10, ;)
        self.assertEqual(len(tokens), 5)
        
        # Check specific tokens
        self.assertEqual(tokens[0]['kind'], 'CRAFT')
        self.assertEqual(tokens[1]['kind'], 'IDENTIFIER')
        self.assertEqual(tokens[1]['value'], 'x')
        self.assertEqual(tokens[2]['kind'], 'OPERATOR')
        self.assertEqual(tokens[2]['value'], '=')
        self.assertEqual(tokens[3]['kind'], 'LITERAL')
        self.assertEqual(tokens[3]['value'], '10')
        self.assertEqual(tokens[4]['kind'], 'DELIMITER')
        self.assertEqual(tokens[4]['value'], ';')
    
    def test_keywords(self):
        code = "craft mine dig enchant diamond cobblestone"
        tokens = self.lexer.tokenize(code)
        
        self.assertEqual(tokens[0]['kind'], 'CRAFT')
        self.assertEqual(tokens[1]['kind'], 'MINE')
        self.assertEqual(tokens[2]['kind'], 'DIG')
        self.assertEqual(tokens[3]['kind'], 'ENCHANT')
        self.assertEqual(tokens[4]['kind'], 'DIAMOND')
        self.assertEqual(tokens[5]['kind'], 'COBBLESTONE')
    
    def test_string_literals(self):
        code = 'craft message = "Hello, Minecraft!";'
        tokens = self.lexer.tokenize(code)
        
        self.assertEqual(tokens[3]['kind'], 'LITERAL')
        self.assertEqual(tokens[3]['value'], 'Hello, Minecraft!')

class TestParser(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        
    def test_declaration(self):
        code = "craft power = 64;"
        tokens = self.lexer.tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertEqual(len(ast), 1)
        self.assertEqual(ast[0]['type'], 'declaration')
        self.assertEqual(ast[0]['identifier'], 'power')
        self.assertEqual(ast[0]['expression']['type'], 'literal')
        self.assertEqual(ast[0]['expression']['value'], '64')
    
    def test_if_statement(self):
        code = "mine (x > 10) { craft y = 20; }"
        tokens = self.lexer.tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertEqual(len(ast), 1)
        self.assertEqual(ast[0]['type'], 'if_statement')
        self.assertEqual(ast[0]['condition']['type'], 'binary_op')
        self.assertEqual(ast[0]['condition']['op'], '>')
        self.assertEqual(len(ast[0]['true_block']), 1)
    
    def test_binary_operation(self):
        code = "craft result = 10 + 20;"
        tokens = self.lexer.tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()
        
        expr = ast[0]['expression']
        self.assertEqual(expr['type'], 'binary_op')
        self.assertEqual(expr['op'], '+')
        self.assertEqual(expr['left']['value'], '10')
        self.assertEqual(expr['right']['value'], '20')
    
    def test_parser_error(self):
        code = "craft x = ;"  # Missing expression
        tokens = self.lexer.tokenize(code)
        parser = Parser(tokens)
        
        with self.assertRaises(CompilerError):
            parser.parse()

class TestTACGenerator(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        
    def test_declaration_tac(self):
        code = "craft power = 64;"
        tokens = self.lexer.tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()
        
        tac_gen = TACGenerator()
        tac = tac_gen.generate(ast)
        
        self.assertIn("power = 64", tac)
    
    def test_binary_op_tac(self):
        code = "craft result = 10 + 20;"
        tokens = self.lexer.tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()
        
        tac_gen = TACGenerator()
        tac = tac_gen.generate(ast)
        
        # Should generate: emerald1 = 10 + 20; result = emerald1
        self.assertIn("emerald1 = 10 + 20", tac)
        self.assertIn("result = emerald1", tac)
    
    def test_if_statement_tac(self):
        code = "craft x = 5; mine (x > 10) { craft y = 20; }"
        tokens = self.lexer.tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()
        
        tac_gen = TACGenerator()
        tac = tac_gen.generate(ast)
        
        # Check for jump labels and instructions
        self.assertTrue(any("if" in line and "goto" in line for line in tac))
        self.assertTrue(any("BIOME_1:" in line for line in tac))
        self.assertTrue(any("y = 20" in line for line in tac))
    
    def test_semantic_error(self):
        code = "craft x = y + 10;"  # y is undeclared
        tokens = self.lexer.tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()
        
        tac_gen = TACGenerator()
        with self.assertRaises(CompilerError):
            tac_gen.generate(ast)

class TestFullCompilation(unittest.TestCase):
    def test_successful_compilation(self):
        code = """
        craft power = 64 + 1;
        mine (power > 64) {
            craft enchantment = "Efficiency V!";
        }
        """
        
        # This should not raise any exceptions
        try:
            lexer = Lexer()
            tokens = lexer.tokenize(code)
            
            parser = Parser(tokens)
            ast = parser.parse()
            
            tac_gen = TACGenerator()
            tac = tac_gen.generate(ast)
            
            # Check a few things in the TAC
            self.assertTrue(any("power" in line for line in tac))
            self.assertTrue(any("64 + 1" in line for line in tac))
            self.assertTrue(any("enchantment" in line for line in tac))
        except CompilerError as e:
            self.fail(f"Compilation raised CompilerError: {e}")
    
    def test_loop_statement(self):
        code = """
        craft counter = 0;
        dig (counter < 5) {
            craft counter = counter + 1;
        }
        """
        
        try:
            lexer = Lexer()
            tokens = lexer.tokenize(code)
            
            parser = Parser(tokens)
            ast = parser.parse()
            
            tac_gen = TACGenerator()
            tac = tac_gen.generate(ast)
            
            # Check for loop-related instructions
            self.assertTrue(any("counter = 0" in line for line in tac))
            self.assertTrue(any("counter < 5" in line for line in tac or "emerald" in line and "< 5" in line))
            self.assertTrue(any("counter + 1" in line for line in tac))
            self.assertTrue(any("goto BIOME_" in line for line in tac))
        except CompilerError as e:
            self.fail(f"Compilation raised CompilerError: {e}")

if __name__ == "__main__":
    unittest.main()