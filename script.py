# Classe para representar um token
class Token:
    def __init__(self, category, value):
        self.category = category
        self.value = value

# Lista de palavras-chave da linguagem
reserved_words = ['END', 'LET', 'GO', 'TO', 'OF', 'READ', 'PRINT', 'IF', 'THEN', 'ELSE']

# Função do analisador léxico
def tokenize(input_string):
    token_collection = []
    index = 0
    while index < len(input_string):
        char = input_string[index]
        if char.isspace():
            index += 1
            continue
        elif char.isalpha():
            word = ''
            while index < len(input_string) and input_string[index].isalnum():
                word += input_string[index]
                index += 1
            if word.upper() in reserved_words:
                token_collection.append(Token('keyword', word.upper()))
            else:
                token_collection.append(Token('ide', word))
        elif char.isdigit():
            number = ''
            while index < len(input_string) and input_string[index].isdigit():
                number += input_string[index]
                index += 1
            token_collection.append(Token('num', number))
        elif char == ':':
            if index + 1 < len(input_string) and input_string[index + 1] == '=':
                token_collection.append(Token('operator', ':='))
                index += 2
            else:
                token_collection.append(Token('punctuation', ':'))
                index += 1
        elif char == '>':
            if index + 1 < len(input_string) and input_string[index + 1] == '=':
                token_collection.append(Token('operator', '>='))
                index += 2
            else:
                token_collection.append(Token('operator', '>'))
                index += 1
        elif char in ['=', '<', '+', '-', '*', '/']:
            token_collection.append(Token('operator', char))
            index += 1
        elif char in [';', ',', '(', ')']:
            token_collection.append(Token('punctuation', char))
            index += 1
        else:
            print(f"Error: invalid character '{char}'")
            index += 1
    return token_collection

# Variáveis globais para o parser
tokens = []
position = 0

# Função para processar expressões aritméticas
def expression():
    global position
    factor()  # Processa o primeiro fator
    while position < len(tokens) and tokens[position].category == 'operator' and tokens[position].value in ['+', '-', '*', '/']:
        op = tokens[position].value
        position += 1
        factor()
        if op in ['*', '/']:  # Prioridade de multiplicação/divisão é tratada implicitamente
            continue

def factor():
    global position
    if position >= len(tokens):
        print("Error: expected identifier, number, or '('")
        return
    current_token = tokens[position]
    if current_token.category in ['ide', 'num']:
        position += 1
    elif current_token.category == 'punctuation' and current_token.value == '(':
        position += 1
        expression()
        if position < len(tokens) and tokens[position].category == 'punctuation' and tokens[position].value == ')':
            position += 1
        else:
            print("Error: expected ')'")
    else:
        print("Error: expected identifier, number, or '('")

# Função para processar sequência de comandos
def command_sequence():
    global position
    while position < len(tokens) and (tokens[position].category != 'keyword' or tokens[position].value != 'END'):
        command()
        if position < len(tokens) and tokens[position].category == 'punctuation' and tokens[position].value == ';':
            position += 1
        else:
            break

# Função para processar comandos
def command():
    global position
    if position >= len(tokens):
        return
    current_token = tokens[position]
    if current_token.category == 'keyword':
        if current_token.value == 'LET':
            position += 1
            if position < len(tokens) and tokens[position].category == 'ide':
                position += 1
                if position < len(tokens) and tokens[position].category == 'operator' and tokens[position].value == ':=':
                    position += 1
                    expression()
                else:
                    print("Error: expected ':='")
            else:
                print("Error: expected identifier")
        elif current_token.value == 'GO':
            position += 1
            if position < len(tokens) and tokens[position].category == 'keyword' and tokens[position].value == 'TO':
                position += 1
                if position < len(tokens):
                    if tokens[position].category == 'ide':
                        position += 1
                    elif tokens[position].category == 'num':
                        position += 1
                        if position < len(tokens) and tokens[position].category == 'keyword' and tokens[position].value == 'OF':
                            position += 1
                            while position < len(tokens) and tokens[position].category == 'ide':
                                position += 1
                                if position < len(tokens) and tokens[position].category == 'punctuation' and tokens[position].value == ',':
                                    position += 1
                                else:
                                    break
                        else:
                            print("Error: expected 'OF'")
                    else:
                        print("Error: expected identifier or number")
                else:
                    print("Error: expected identifier or number")
            else:
                print("Error: expected 'TO'")
        elif current_token.value == 'READ':
            position += 1
            while position < len(tokens) and tokens[position].category == 'ide':
                position += 1
                if position < len(tokens) and tokens[position].category == 'punctuation' and tokens[position].value == ',':
                    position += 1
                else:
                    break
            if position >= len(tokens) or tokens[position-1].category != 'ide':
                print("Error: expected identifier")
        elif current_token.value == 'PRINT':
            position += 1
            expression()
            while position < len(tokens) and tokens[position].category == 'punctuation' and tokens[position].value == ',':
                position += 1
                expression()
        elif current_token.value == 'IF':
            position += 1
            expression()
            if position < len(tokens) and tokens[position].category == 'operator' and tokens[position].value in ['=', '>', '>=', '<']:
                position += 1
                expression()
                if position < len(tokens) and tokens[position].category == 'keyword' and tokens[position].value == 'THEN':
                    position += 1
                    command()
                    if position < len(tokens) and tokens[position].category == 'keyword' and tokens[position].value == 'ELSE':
                        position += 1
                        command()
                    else:
                        print("Error: expected 'ELSE'")
                else:
                    print("Error: expected 'THEN'")
            else:
                print("Error: expected comparison operator")
    elif current_token.category == 'ide' and position + 1 < len(tokens) and tokens[position + 1].category == 'punctuation' and tokens[position + 1].value == ':':
        position += 2  # Consome rótulo e ':'
        command()

# Teste do analisador
if __name__ == "__main__":
    sample_input = "LET A := 1 + 2; PRINT A; END"
    tokens = tokenize(sample_input)
    position = 0
    command_sequence()
    if position < len(tokens) and tokens[position].category == 'keyword' and tokens[position].value == 'END':
        position += 1
        if position == len(tokens):
            print("Análise sintática bem-sucedida")
        else:
            print("Erro na análise sintática: tokens extras")
    else:
        print("Erro na análise sintática: esperado 'END'")