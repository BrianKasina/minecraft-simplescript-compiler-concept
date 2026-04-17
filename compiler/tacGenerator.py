from compiler.errors import SemanticError 

class TACGenerator:
    def __init__(self):
        # This is the Three-Address Code Generator class responsible for transforming the parsed Abstract Syntax Tree
        # into an intermediate representation that's closer to machine code 
        # TAC is a form where each instruction has at most three operands eg, x = y + z
        # This simplifies complex expressions into a sequence of simpler instructions that can be handled much easier during compilation
        

        ...
        #this section handles four important roles, first  counters are created, one for temporary variable names, another for labeling control
        #flow statements and the a list to store the generated TAC, and lastly a set to keep track of the declared variables in the source code.
        ...
        self.temp_counter = 0 
        self.label_counter = 0
        self.code = []
        self.symbols = set()

    def new_temp(self):
        # Creates a unique temporary variable name with a Minecraft theme  which are used to store intermediate values during computation
        # such as emerald1, emerald2, etc.
        self.temp_counter += 1
        return f"emerald{self.temp_counter}"

    def new_label(self):
        # Creates a unique label for marking positions in code which will then be used in the code to represent destinations for goto statements 
        # things like go to, jump to etc.
        self.label_counter += 1
        return f"BIOME_{self.label_counter}" 

    def generate(self, node):
        # This is the main recursive function that processes each node of the abstract syntax tree  and generates appropriate three address code
        #different nodes may require different representations which is why each is treated differently
        
        if isinstance(node, list):
            for n in node:
                self.generate(n)
            return self.code

        if node['type'] == 'declaration':
            var_name = node['identifier']
            self.symbols.add(var_name)
            expr_temp = self.generate(node['expression'])  
            self.code.append(f"{var_name} = {expr_temp}")
            

        elif node['type'] == 'identifier':
            var_name = node['name']
            if var_name not in self.symbols:
                raise SemanticError(f"Undecrafted variable '{var_name}'")  
            return var_name 

        elif node['type'] == 'binary_op':
            left_temp = self.generate(node['left']) 
            right_temp = self.generate(node['right']) 
            result_temp = self.new_temp() 
            self.code.append(f"{result_temp} = {left_temp} {node['op']} {right_temp}")
            return result_temp

        elif node['type'] == 'literal':
            return node['value']
        
        elif node['type'] == 'if_statement':
            condition_temp = self.generate(node['condition'])
            true_label = self.new_label() 
            false_label = self.new_label()
            end_label = self.new_label()
            
            # Implement the conditional jumping logic using the goto statement
            self.code.append(f"if {condition_temp} goto {true_label}")
            self.code.append(f"goto {false_label}") 
            
            # If the condition is true in the if statement
            self.code.append(f"{true_label}:") 
            self.generate(node['true_block']) 
            self.code.append(f"goto {end_label}") 
            
            # if the condition is false, this is the fallback code, ie, the else block
            self.code.append(f"{false_label}:") 
            if 'false_block' in node:
                self.generate(node['false_block']) 
            
            # End of if statement
            self.code.append(f"{end_label}:")
        
        elif node['type'] == 'while_statement':
            start_label = self.new_label() 
            end_label = self.new_label()  
            
            
            self.code.append(f"{start_label}:")
            condition_temp = self.generate(node['condition'])
            self.code.append(f"if {condition_temp} goto {end_label}")
            self.generate(node['body']) 
            self.code.append(f"goto {start_label}")
            self.code.append(f"{end_label}:")

        elif node['type'] == 'function_call':
            func_name = node['name']
            args = [self.generate(arg) for arg in node['args']]
            self.code.append(f"call {func_name}({', '.join(args)})")

        elif node['type'] == 'return_statement':
            return_temp = self.generate(node['value'])
            self.code.append(f"return {return_temp}")

        elif node['type'] == 'print_statement':
            value_temp = self.generate(node['value'])
            self.code.append(f"print {value_temp}") 