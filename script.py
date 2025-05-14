import re

# Classe Token
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

# Palavras-chave
keywords = ["LET", "GO", "TO", "READ", "PRINT", "IF", "THEN", "ELSE", "END"]

# Especificações dos tokens
token_specs = [
    ("NUMBER", r'\d+'),              # Números
    ("IDENTIFIER", r'[A-Z][A-Z0-9]*'),  # Identificadores
    ("ASSIGN", r':='),               # Operador de atribuição
    ("PLUS", r'\+'),                 # Operador de soma
    ("MINUS", r'-'),                 # Operador de subtração
    ("STAR", r'\*'),                 # Operador de multiplicação
    ("SLASH", r'/'),                 # Operador de divisão
    ("EQ", r'='),                    # Operador de igualdade
    ("GT", r'>'),                    # Operador maior que
    ("LT", r'<'),                    # Operador menor que
    ("LPAREN", r'\('),               # Parêntese esquerdo
    ("RPAREN", r'\)'),               # Parêntese direito
    ("SEMI", r';'),                  # Ponto e vírgula
    ("COLON", r':'),                 # Dois pontos
    ("COMMA", r','),                 # Vírgula
    ("WHITESPACE", r'\s+'),          # Espaço em branco (ignorado)
]

# Função de erro
def error(message):
    print(f"Erro: {message}")
    exit(1)

# Função do analisador léxico
def lexer(input_string):
    tokens = []
    pos = 0
    while pos < len(input_string):
        match = None
        for type, pattern in token_specs:
            regex = re.compile(pattern)
            match = regex.match(input_string, pos)
            if match:
                text = match.group(0)
                if type == "IDENTIFIER":
                    if text in keywords:
                        tokens.append(Token(text, text))
                    else:
                        tokens.append(Token("IDENTIFIER", text))
                elif type != "WHITESPACE":
                    tokens.append(Token(type, text))
                pos = match.end(0)
                break
        if not match:
            error(f"Caractere inválido na posição {pos}: '{input_string[pos]}'")
    return tokens

# Variáveis globais para o analisador sintático
tokens = []
pos = 0

# Funções auxiliares
def current_token():
    return tokens[pos] if pos < len(tokens) else None

def match(expected_type):
    global pos
    if pos < len(tokens) and tokens[pos].type == expected_type:
        pos += 1
        return True
    return False

# Funções do analisador sintático
def programa():
    sequencia_de_comandos()
    if not match("END"):
        error("Esperado END")
    if pos != len(tokens):
        error("Tokens extras após END")

def sequencia_de_comandos():
    comando()
    sequencia_de_comandos_linha()

def sequencia_de_comandos_linha():
    if match("SEMI"):
        comando()
        sequencia_de_comandos_linha()

def comando():
    if current_token() is None:
        return
    if current_token().type == "LET":
        atribuicao()
    elif current_token().type == "GO":
        desvio()
    elif current_token().type == "READ":
        leitura()
    elif current_token().type == "PRINT":
        impressao()
    elif current_token().type == "IF":
        decisao()
    elif (current_token().type == "IDENTIFIER" and 
          pos + 1 < len(tokens) and tokens[pos + 1].type == "COLON"):
        match("IDENTIFIER")
        match("COLON")
        comando()
    # Caso epsilon, não faz nada

def atribuicao():
    if not match("LET"):
        error("Esperado LET")
    if not match("IDENTIFIER"):
        error("Esperado identificador")
    if not match("ASSIGN"):
        error("Esperado :=")
    expressao()

def expressao():
    termo()
    expressao_linha()

def expressao_linha():
    if match("PLUS"):
        termo()
        expressao_linha()
    elif match("MINUS"):
        termo()
        expressao_linha()

def termo():
    fator()
    termo_linha()

def termo_linha():
    if match("STAR"):
        fator()
        termo_linha()
    elif match("SLASH"):
        fator()
        termo_linha()

def fator():
    if match("IDENTIFIER"):
        pass
    elif match("NUMBER"):
        pass
    elif match("LPAREN"):
        expressao()
        if not match("RPAREN"):
            error("Esperado )")
    else:
        error("Esperado identificador, número ou (")

def desvio():
    if not match("GO"):
        error("Esperado GO")
    if not match("TO"):
        error("Esperado TO")
    token_atual = current_token()
    if token_atual is None or token_atual.type != "IDENTIFIER":
        error("Esperado identificador após GO TO")
    match("IDENTIFIER")

def leitura():
    if not match("READ"):
        error("Esperado READ")
    lista_de_identificadores()

def lista_de_identificadores():
    if current_token() and current_token().type == "IDENTIFIER":
        match("IDENTIFIER")
        while match("COMMA"):
            if not match("IDENTIFIER"):
                error("Esperado identificador após vírgula")

def impressao():
    if not match("PRINT"):
        error("Esperado PRINT")
    lista_de_expressoes()

def lista_de_expressoes():
    if current_token() and current_token().type in ["IDENTIFIER", "NUMBER", "LPAREN"]:
        expressao()
        while match("COMMA"):
            expressao()

def decisao():
    if not match("IF"):
        error("Esperado IF")
    comparacao()
    if not match("THEN"):
        error("Esperado THEN")

    if current_token() is not None and current_token().type == "ELSE":
        error("Comando esperado após THEN e antes de ELSE")
    comando()  
    if not match("ELSE"):
        error("Esperado ELSE após o comando da cláusula THEN") 

    comando()

def comparacao():
    expressao()
    if not (match("EQ") or match("GT") or match("LT")):
        error("Esperado =, > ou <")
    expressao()

# Bloco principal
if __name__ == "__main__":
    input_string = input("Digite o código: ")
    tokens = lexer(input_string)
    pos = 0
    try:
        programa()
        print("Análise concluída com sucesso")
    except SystemExit:
        pass  # Erro já foi tratado pela função error()