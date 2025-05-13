class Token:
    def __init__(self, value, category):
        self.value = value
        self.category = category

def analyze_syntax(token_list, current_pos=0):
    """Analisa a sintaxe de um programa completo, esperando comandos e um 'END' no final."""
    current_pos = process_commands(token_list, current_pos)
    if current_pos < len(token_list) and token_list[current_pos].value == 'END':
        current_pos += 1
    else:
        print(f"Erro de Sintaxe: Esperado 'END' na posição {current_pos}")
    if current_pos < len(token_list):
        print(f"Erro de Sintaxe: Tokens extras após 'END' na posição {current_pos}")
    return current_pos

def process_commands(token_list, current_pos):
    """Processa uma sequência de comandos separados por ';'."""
    while current_pos < len(token_list) and token_list[current_pos].value != 'END':
        current_pos = handle_command(token_list, current_pos)
        if current_pos < len(token_list) and token_list[current_pos].value == ';':
            current_pos += 1
        else:
            break
    return current_pos

def handle_command(token_list, current_pos):
    """Analisa um comando individual, como atribuição, leitura ou condicional."""
    if current_pos >= len(token_list) or token_list[current_pos].value == 'END':
        return current_pos
    current_token = token_list[current_pos]
    if current_token.value == 'LET':
        current_pos = process_assignment(token_list, current_pos)
    elif current_token.value == 'GO':
        current_pos = process_goto(token_list, current_pos)
    elif current_token.value == 'READ':
        current_pos = process_read(token_list, current_pos)
    elif current_token.value == 'PRINT':
        current_pos = process_print(token_list, current_pos)
    elif current_token.value == 'IF':
        current_pos = process_conditional(token_list, current_pos)
    elif current_token.category == 'ide' and current_pos + 1 < len(token_list) and token_list[current_pos + 1].value == ':':
        current_pos = process_label(token_list, current_pos)
        current_pos += 1  # consome o ':'
        current_pos = handle_command(token_list, current_pos)
    else:
        return current_pos
    return current_pos

def process_assignment(token_list, current_pos):
    """Analisa uma atribuição do tipo: LET identificador := expressão."""
    if token_list[current_pos].value == 'LET':
        current_pos += 1
        current_pos = check_identifier(token_list, current_pos)
        if current_pos < len(token_list) and token_list[current_pos].value == ':=':
            current_pos += 1
            current_pos = evaluate_expression(token_list, current_pos)
        else:
            print(f"Erro de Sintaxe: Esperado ':=' na posição {current_pos}")
    return current_pos

def evaluate_expression(token_list, current_pos):
    """Avalia uma expressão composta por termos e operadores."""
    current_pos = process_term(token_list, current_pos)
    current_pos = extend_expression(token_list, current_pos)
    return current_pos

def extend_expression(token_list, current_pos):
    """Analisa a continuação de uma expressão com '+' ou '-'."""
    if current_pos < len(token_list) and token_list[current_pos].value in ['+', '-']:
        current_pos += 1
        current_pos = process_term(token_list, current_pos)
        current_pos = extend_expression(token_list, current_pos)
    return current_pos

def process_term(token_list, current_pos):
    """Processa um termo, que pode incluir fatores e multiplicação/divisão."""
    current_pos = process_factor(token_list, current_pos)
    current_pos = extend_term(token_list, current_pos)
    return current_pos

def extend_term(token_list, current_pos):
    """Analisa a continuação de um termo com '*' ou '/'."""
    if current_pos < len(token_list) and token_list[current_pos].value in ['*', '/']:
        current_pos += 1
        current_pos = process_factor(token_list, current_pos)
        current_pos = extend_term(token_list, current_pos)
    return current_pos

def process_factor(token_list, current_pos):
    """Analisa um fator: identificador, número ou expressão entre parênteses."""
    if current_pos < len(token_list):
        if token_list[current_pos].category == 'ide':
            current_pos = check_identifier(token_list, current_pos)
        elif token_list[current_pos].category == 'num':
            current_pos = check_number(token_list, current_pos)
        elif token_list[current_pos].value == '(':
            current_pos += 1
            current_pos = evaluate_expression(token_list, current_pos)
            if current_pos < len(token_list) and token_list[current_pos].value == ')':
                current_pos += 1
            else:
                print(f"Erro de Sintaxe: Esperado ')' na posição {current_pos}")
        else:
            print(f"Erro de Sintaxe: Esperado identificador, número ou '(' na posição {current_pos}")
    return current_pos

def process_goto(token_list, current_pos):
    """Analisa um comando GO TO: rótulo ou número seguido de lista de rótulos."""
    if token_list[current_pos].value == 'GO':
        current_pos += 1
        if token_list[current_pos].value == 'TO':
            current_pos += 1
            if token_list[current_pos].category == 'ide':
                current_pos = process_label(token_list, current_pos)
            elif token_list[current_pos].category == 'num':
                current_pos = check_number(token_list, current_pos)
                if token_list[current_pos].value == 'OF':
                    current_pos += 1
                    current_pos = process_label_sequence(token_list, current_pos)
                else:
                    print(f"Erro de Sintaxe: Esperado 'OF' na posição {current_pos}")
    return current_pos

def process_label_sequence(token_list, current_pos):
    """Analisa uma sequência de rótulos separados por vírgulas."""
    current_pos = process_label(token_list, current_pos)
    while current_pos < len(token_list) and token_list[current_pos].value == ',':
        current_pos += 1
        current_pos = process_label(token_list, current_pos)
    return current_pos

def process_label(token_list, current_pos):
    """Verifica se o token é um rótulo válido (identificador)."""
    return check_identifier(token_list, current_pos)

def process_read(token_list, current_pos):
    """Analisa um comando READ seguido de uma lista de identificadores."""
    if token_list[current_pos].value == 'READ':
        current_pos += 1
        current_pos = process_identifier_list(token_list, current_pos)
    return current_pos

def process_identifier_list(token_list, current_pos):
    """Analisa uma lista de identificadores separados por vírgulas."""
    current_pos = check_identifier(token_list, current_pos)
    while current_pos < len(token_list) and token_list[current_pos].value == ',':
        current_pos += 1
        current_pos = check_identifier(token_list, current_pos)
    return current_pos

def process_print(token_list, current_pos):
    """Analisa um comando PRINT seguido de uma lista de expressões."""
    if token_list[current_pos].value == 'PRINT':
        current_pos += 1
        current_pos = process_expression_list(token_list, current_pos)
    return current_pos

def process_expression_list(token_list, current_pos):
    """Analisa uma lista de expressões separadas por vírgulas."""
    current_pos = evaluate_expression(token_list, current_pos)
    while current_pos < len(token_list) and token_list[current_pos].value == ',':
        current_pos += 1
        current_pos = evaluate_expression(token_list, current_pos)
    return current_pos

def process_conditional(token_list, current_pos):
    """Analisa um comando IF com comparação, THEN e ELSE."""
    if token_list[current_pos].value == 'IF':
        current_pos += 1
        current_pos = check_comparison(token_list, current_pos)
        if token_list[current_pos].value == 'THEN':
            current_pos += 1
            current_pos = handle_command(token_list, current_pos)
            if token_list[current_pos].value == 'ELSE':
                current_pos += 1
                current_pos = handle_command(token_list, current_pos)
            else:
                print(f"Erro de Sintaxe: Esperado 'ELSE' na posição {current_pos}")
    return current_pos

def check_comparison(token_list, current_pos):
    """Analisa uma comparação entre duas expressões."""
    current_pos = evaluate_expression(token_list, current_pos)
    current_pos = check_operator(token_list, current_pos)
    current_pos = evaluate_expression(token_list, current_pos)
    return current_pos

def check_operator(token_list, current_pos):
    """Verifica se o token é um operador de comparação válido."""
    if token_list[current_pos].value in ['=', '>', '>=', '<']:
        current_pos += 1
    else:
        print(f"Erro de Sintaxe: Operador de comparação inválido na posição {current_pos}")
    return current_pos

def check_identifier(token_list, current_pos):
    """Verifica se o token é um identificador válido."""
    if current_pos < len(token_list) and token_list[current_pos].category == 'ide':
        current_pos += 1
    else:
        print(f"Erro de Sintaxe: Esperado identificador na posição {current_pos}")
    return current_pos

def check_number(token_list, current_pos):
    """Verifica se o token é um número válido."""
    if current_pos < len(token_list) and token_list[current_pos].category == 'num':
        current_pos += 1
    else:
        print(f"Erro de Sintaxe: Esperado número na posição {current_pos}")
    return current_pos

# Teste do analisador
if __name__ == "__main__":
    example_tokens = [
        Token('LET', 'keyword'), Token('x', 'ide'), Token(':=', 'operator'),
        Token('1', 'num'), Token('+', 'operator'), Token('2', 'num'), Token(';', 'punctuation'),
        Token('END', 'keyword')
    ]
    final_position = analyze_syntax(example_tokens)
    if final_position == len(example_tokens):
        print("Análise concluída com sucesso!")
    else:
        print("Falha na análise sintática.")