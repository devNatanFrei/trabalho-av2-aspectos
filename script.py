# Classe para representar um token
class Token:
    def __init__(self, category, value):
        self.category = category
        self.value = value

    def __repr__(self): # Adicionado para facilitar a depuração de listas de tokens
        return f"Token({self.category}, '{self.value}')"

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
        elif char in ['=', '<', '+', '-', '*', '/']: # Adicionado '<=' como operador
            if char == '<' and index + 1 < len(input_string) and input_string[index + 1] == '=':
                token_collection.append(Token('operator', '<='))
                index += 2
            else:
                token_collection.append(Token('operator', char))
                index += 1
        elif char in [';', ',', '(', ')']:
            token_collection.append(Token('punctuation', char))
            index += 1
        else:
            print(f"Erro: caractere inválido '{char}'")
            return None  # Retorna None para indicar erro léxico
    return token_collection

# Variáveis globais para o parser
tokens = []
position = 0
labels_defined = set()  # Conjunto para armazenar rótulos definidos
error_found = False  # Flag para indicar erro

# Função para processar expressões aritméticas
def expression():
    global position, error_found
    if error_found or position >= len(tokens):
        return
    factor()
    while position < len(tokens) and tokens[position].category == 'operator' and tokens[position].value in ['+', '-', '*', '/']:
        position += 1
        factor()

def factor():
    global position, error_found
    if error_found or position >= len(tokens):
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
            print("Erro: esperado ')'")
            error_found = True
    else:
        print("Erro: esperado identificador, número ou '('")
        error_found = True

# Função para processar sequência de comandos
def command_sequence():
    global position, error_found
    while position < len(tokens) and not error_found and \
          (tokens[position].category != 'keyword' or tokens[position].value != 'END'):
        command()
        if error_found: # Se um comando deu erro, não tente ler ';'
            break
        if position < len(tokens) and tokens[position].category == 'punctuation' and tokens[position].value == ';':
            position += 1
        # Se o próximo token não for ';' e não for END, e não houver erro,
        # então é um erro de sequência de comandos (ex: comando comando SEM ';')
        # Mas isso é melhor tratado no final do parse se não chegou ao END.
        elif position < len(tokens) and (tokens[position].category != 'keyword' or tokens[position].value != 'END'):
            # Isso indica que um comando terminou e o próximo token não é ';' nem 'END'.
            # Isso será pego pela verificação final no parse().
            break
        else: # Chegou ao END ou fim dos tokens
            break


# Função para processar comandos
def command():
    global position, labels_defined, error_found
    if error_found or position >= len(tokens):
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
                    if error_found: return # Erro na expressão, não continuar
                else:
                    print("Erro: esperado ':='")
                    error_found = True
            else:
                print("Erro: esperado identificador")
                error_found = True
        elif current_token.value == 'GO':
            position += 1
            if position < len(tokens) and tokens[position].category == 'keyword' and tokens[position].value == 'TO':
                position += 1
                if position < len(tokens):
                    if tokens[position].category == 'ide': # GO TO <label>
                        position += 1
                    elif tokens[position].category == 'num': # GO TO <num> OF ...
                        num_value_str = tokens[position].value
                        position += 1
                        if position < len(tokens) and tokens[position].category == 'keyword' and tokens[position].value == 'OF':
                            position += 1
                            label_list = []
                            # Espera-se pelo menos um rótulo
                            if position < len(tokens) and tokens[position].category == 'ide':
                                while position < len(tokens) and tokens[position].category == 'ide':
                                    label_list.append(tokens[position].value)
                                    position += 1
                                    if position < len(tokens) and tokens[position].category == 'punctuation' and tokens[position].value == ',':
                                        position += 1
                                        # Após uma vírgula, deve vir outro identificador
                                        if not (position < len(tokens) and tokens[position].category == 'ide'):
                                            print("Erro: esperado identificador após ',' em lista de rótulos")
                                            error_found = True
                                            return
                                    else:
                                        break
                                if not error_found:
                                    try:
                                        num_value = int(num_value_str)
                                        if num_value < 1 or num_value > len(label_list):
                                            print(f"Erro: número inválido '{num_value}' em 'GO TO', deve ser entre 1 e {len(label_list)}")
                                            error_found = True
                                    except ValueError: # Caso o 'num' não seja um inteiro válido (improvável com o lexer atual)
                                        print(f"Erro: valor numérico inválido '{num_value_str}'")
                                        error_found = True
                            else:
                                print("Erro: esperado identificador na lista de rótulos após 'OF'")
                                error_found = True
                        else:
                            print("Erro: esperado 'OF'")
                            error_found = True
                    else:
                        print("Erro: esperado identificador ou número após 'GO TO'")
                        error_found = True
                else:
                    print("Erro: esperado identificador ou número após 'GO TO'")
                    error_found = True
            else:
                print("Erro: esperado 'TO'")
                error_found = True
        elif current_token.value == 'READ':
            position += 1
            # Espera-se pelo menos um identificador
            if position < len(tokens) and tokens[position].category == 'ide':
                while position < len(tokens) and tokens[position].category == 'ide':
                    position += 1
                    if position < len(tokens) and tokens[position].category == 'punctuation' and tokens[position].value == ',':
                        position += 1
                         # Após uma vírgula, deve vir outro identificador
                        if not (position < len(tokens) and tokens[position].category == 'ide'):
                            print("Erro: esperado identificador após ',' em lista de READ")
                            error_found = True
                            return
                    else:
                        break
            else: # Nenhum identificador após READ
                print("Erro: esperado identificador após 'READ'")
                error_found = True

        elif current_token.value == 'PRINT':
            position += 1
            # Espera-se pelo menos uma expressão
            if position < len(tokens):
                expression()
                if error_found: return
                while position < len(tokens) and tokens[position].category == 'punctuation' and tokens[position].value == ',':
                    position += 1
                    # Após uma vírgula, deve vir outra expressão
                    if position < len(tokens):
                        expression()
                        if error_found: return
                    else:
                        print("Erro: esperada expressão após ',' em PRINT")
                        error_found = True
                        return
            else:
                print("Erro: esperada expressão após 'PRINT'")
                error_found = True

        elif current_token.value == 'IF':
            position += 1
            expression()
            if error_found: return
            if position < len(tokens) and tokens[position].category == 'operator' and tokens[position].value in ['=', '>', '>=', '<', '<=']: # Adicionado <=
                position += 1
                expression()
                if error_found: return
                if position < len(tokens) and tokens[position].category == 'keyword' and tokens[position].value == 'THEN':
                    position += 1
                    command() # Comando do THEN
                    if error_found: return
                    if position < len(tokens) and tokens[position].category == 'keyword' and tokens[position].value == 'ELSE':
                        position += 1
                        command() # Comando do ELSE
                        if error_found: return
                    else:
                        print("Erro: esperado 'ELSE'")
                        error_found = True
                else:
                    print("Erro: esperado 'THEN'")
                    error_found = True
            else:
                print("Erro: esperado operador de comparação")
                error_found = True
        # END não é um comando, é um terminador de programa. Será tratado pelo parse().
        # Se 'END' for encontrado aqui, é um erro de comando inesperado ou programa vazio.
        elif current_token.value == 'END':
            # Se o comando atual é END, e não estamos no loop principal de command_sequence,
            # isso pode ser um erro se não for o final do programa.
            # No entanto, a lógica de command_sequence já verifica isso.
            # Apenas não avançamos a posição aqui.
            pass


    elif current_token.category == 'ide' and position + 1 < len(tokens) and \
         tokens[position + 1].category == 'punctuation' and tokens[position + 1].value == ':':
        label = current_token.value
        if label in labels_defined:
            print(f"Erro: rótulo '{label}' duplicado")
            error_found = True
            return # Não processar mais após rótulo duplicado
        else:
            labels_defined.add(label)
        position += 2  # Consome rótulo e ':'
        command() # Comando após o rótulo
    else:
        # Se não for uma keyword conhecida nem um label:comando, então é um erro.
        # Isso pode acontecer se houver um token inesperado no início de um comando.
        print(f"Erro: comando inválido ou token inesperado '{current_token.value}'")
        error_found = True


# Função principal do parser
def parse(input_string):
    global tokens, position, labels_defined, error_found
    print(f"\nAnalisando: \"{input_string}\"")
    tokens = tokenize(input_string)
    if tokens is None:
        print("Erro na análise léxica. Análise sintática abortada.")
        return

    position = 0
    labels_defined.clear()
    error_found = False

    # Um programa pode ser apenas END
    if not tokens: # String vazia -> tokens vazios
        print("Erro na análise sintática: entrada vazia, esperado 'END'")
        return

    if len(tokens) == 1 and tokens[0].category == 'keyword' and tokens[0].value == 'END':
        print("Análise sintática bem-sucedida")
        return

    command_sequence()

    if not error_found:
        if position < len(tokens) and tokens[position].category == 'keyword' and tokens[position].value == 'END':
            position += 1
            if position == len(tokens):
                print("Análise sintática bem-sucedida")
            else:
                print(f"Erro na análise sintática: tokens extras após 'END' (próximo token: {tokens[position].value})")
        else:
            if position >= len(tokens) and not error_found: # Chegou ao fim dos tokens sem erro, mas sem END
                 print("Erro na análise sintática: esperado 'END' no final do programa")
            elif not error_found: # Não chegou ao END, mas há tokens restantes
                print(f"Erro na análise sintática: esperado 'END' ou ';' ou comando inválido próximo de '{tokens[position].value if position < len(tokens) else 'FIM'}'")
            # Se error_found já é True, a mensagem específica já foi impressa
    elif error_found:
        # A mensagem de erro específica já foi impressa pela função que detectou o erro.
        # Podemos adicionar uma mensagem genérica aqui se quisermos, mas pode ser redundante.
        print("Análise sintática falhou devido a erro(s) anterior(es).")


# Testes
if __name__ == "__main__":
    # Testes originais
    print("--- Testes Originais ---")
    parse("L1: LET A := 1; L1: PRINT A; END")
    parse("GO TO 0 OF L1, L2; L1: PRINT 1; L2: PRINT 2; END")
    # parse("LET A := 5; PRINT A; END") # Removido o (1) que causava erro na chamada

    print("\n--- Casos de Teste Adicionais ---")

    print("\n--- A. Entradas Válidas ---")
    parse("END")
    parse("LET X := 10; PRINT X + 5; END")
    parse("READ VAL; IF VAL > 0 THEN PRINT VAL ELSE PRINT 0 - VAL; END")
    parse("L1: READ A, B; GO TO L1; END")
    parse("GO TO 2 OF LABEL1, LABEL2, LABEL3; LABEL1: PRINT 1; LABEL2: PRINT 2; LABEL3: PRINT 3; END")
    parse("LET RESULT := (A + B) * (C - D / 2); PRINT RESULT; END")
    parse("START: IF X = Y THEN LET Z := 1 ELSE LET Z := 0; PRINT Z; END")
    parse("PRINT A,B,C; END")
    parse("IF A <= B THEN PRINT A ELSE PRINT B; END") # Testando <=

    print("\n--- B. Erros Léxicos ---")
    parse("LET VAR$ := 10; END")

    print("\n--- C. Erros Sintáticos (Estruturais) ---")
    parse("LET X = 10; END")
    parse("IF A > B THEN PRINT A END")
    parse("PRINT A B; END") # Este caso pode ser interpretado de forma diferente dependendo da recuperação de erro
    parse("READ X, ; END")
    parse("GO TO ; END")
    parse("LET A := 1 PRINT B := 2; END")
    parse("LET A := (1 + 2; END")
    parse("L1: LET X := 10; GO TO OF L2; END")
    parse("LET A := 1; LET B := 2")
    parse("PRINT A+; END")
    parse("IF A > B THEN ; ELSE PRINT B; END") # Comando vazio no THEN (permitido pela gramática?)
                                             # O 'command()' atual não trata 'e' explicitamente.
                                             # Ele falhará esperando um comando válido.
    parse("IF A > B THEN PRINT A ELSE ; END") # Comando vazio no ELSE
    parse("L1: ; END") # Label seguido de comando vazio

    print("\n--- D. Erros Semânticos (Lógica detectada pelo parser) ---")
    parse("GO TO 3 OF L1, L2; L1: PRINT 1; L2: PRINT 2; END")
    parse("LBL: PRINT 1; LBL: PRINT 2; END") # Já testado no original

    print("\n--- E. Casos Limites e Específicos ---")
    parse("LET A := 1;; END")
    parse("READ ; END")
    parse("IF A < B THEN GO TO L1 ELSE GO TO L2; L1: PRINT A; L2: PRINT B; END EXTRA_TOKEN")
    parse("GO TO 1 OF LBL; LBL: PRINT \"OK\"; END") # Erro léxico em "
    parse("") # String vazia
    parse("LET A:=1;END") # Sem espaços
    parse("   LET    A  :=  1 ;  PRINT   A  ;  END   ") # Muitos espaços
    parse("GO TO 1 OF ; END") # GO TO num OF sem lista de rótulos
    parse("GO TO 1 OF L1, ; END") # GO TO num OF com vírgula extra no final da lista

    print("\n--- Testes Adicionais de Lógica ---")
    parse("IF X THEN PRINT Y ELSE PRINT Z; END") # 'X' sozinho não é uma comparação válida
    parse("LET A := B C; END") # Expressão inválida
    parse("L1: READ X Y; END") # READ X, Y esperado
    parse("PRINT ,A; END") # Vírgula no início da lista de expressões
    parse("PRINT A,; END") # Vírgula no final da lista de expressões