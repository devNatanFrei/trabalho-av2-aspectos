import re
import sys # Para usar sys.exit() que é mais comum em Python do que exit(1)

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, '{self.value}')"

class LexerError(Exception):
    pass

class ParseError(Exception):
    pass

class SingleFileParser:
    def __init__(self):
        self.token_specs = [
            ("NUMBER",     r'\d+'),
            ("IDENTIFIER", r'[A-Z][A-Z0-9]*'),
            ("ASSIGN",     r':='),
            ("PLUS",       r'\+'),
            ("MINUS",      r'-'),
            ("STAR",       r'\*'),
            ("SLASH",      r'/'),
            ("EQ",         r'='),
            ("GT",         r'>'),
            ("LT",         r'<'),
            ("LPAREN",     r'\('),
            ("RPAREN",     r'\)'),
            ("SEMI",       r';'),
            ("COLON",      r':'),
            ("COMMA",      r','),
            ("WHITESPACE", r'\s+'),
        ]
        self.keywords = {"LET", "GO", "TO", "READ", "PRINT", "IF", "THEN", "ELSE", "END"}
        self.tokens = []
        self.current_pos = 0

    def _tokenize(self, input_string):
        generated_tokens = []
        current_input_pos = 0
        input_length = len(input_string)

        while current_input_pos < input_length:
            matched = False
            for token_type, pattern_str in self.token_specs:
                pattern = re.compile(pattern_str)
                match = pattern.match(input_string, current_input_pos)
                if match:
                    text = match.group(0)
                    if token_type == "IDENTIFIER":
                        if text in self.keywords:
                            generated_tokens.append(Token(text, text))
                        else:
                            generated_tokens.append(Token("IDENTIFIER", text))
                    elif token_type != "WHITESPACE":
                        generated_tokens.append(Token(token_type, text))
                    
                    current_input_pos = match.end(0)
                    matched = True
                    break
            if not matched:
                raise LexerError(f"Caractere inválido na posição {current_input_pos}: '{input_string[current_input_pos]}'")
        return generated_tokens

    def _current_token(self):
        if self.current_pos < len(self.tokens):
            return self.tokens[self.current_pos]
        return None

    def _match_token(self, expected_type):
        token = self._current_token()
        if token and token.type == expected_type:
            self.current_pos += 1
            return True
        return False

    def _error(self, message):
        token_info = ""
        if self._current_token():
            token_info = f" (próximo token: {self._current_token()})"
        raise ParseError(f"Erro: {message}{token_info} na posição do token {self.current_pos}.")

    def parse(self, input_code):
        self.tokens = self._tokenize(input_code)
        self.current_pos = 0
        self._parse_programa()

    def _parse_programa(self):
        self._parse_sequencia_de_comandos()
        if not self._match_token("END"):
            self._error("Esperado 'END' no final do programa")
        if self._current_token() is not None:
            self._error("Tokens extras após 'END'")

    def _parse_sequencia_de_comandos(self):
        self._parse_comando()
        self._parse_sequencia_de_comandos_linha()

    def _parse_sequencia_de_comandos_linha(self):
        token = self._current_token()
        if token and token.type == "SEMI":
            self._match_token("SEMI")
            self._parse_comando()
            self._parse_sequencia_de_comandos_linha()

    def _parse_comando(self):
        token = self._current_token()
        if token is None:
            return

        if token.type == "LET":
            self._parse_atribuicao()
        elif token.type == "GO":
            self._parse_desvio()
        elif token.type == "READ":
            self._parse_leitura()
        elif token.type == "PRINT":
            self._parse_impressao()
        elif token.type == "IF":
            self._parse_decisao()
        elif token.type == "IDENTIFIER" and \
             self.current_pos + 1 < len(self.tokens) and \
             self.tokens[self.current_pos + 1].type == "COLON":
            self._match_token("IDENTIFIER")
            self._match_token("COLON")
            self._parse_comando()
        elif token.type in {"END", "ELSE", "THEN", "SEMI"}:
            pass
        else:
            # Se não for um comando conhecido e a regra chamadora espera um,
            # o erro será pego pela falha em `_match_token` na regra chamadora.
            pass


    def _parse_atribuicao(self):
        if not self._match_token("LET"): self._error("Esperado 'LET' para atribuição")
        if not self._match_token("IDENTIFIER"): self._error("Esperado identificador após 'LET'")
        if not self._match_token("ASSIGN"): self._error("Esperado ':=' após identificador na atribuição")
        self._parse_expressao()

    def _parse_expressao(self):
        self._parse_termo()
        self._parse_expressao_linha()

    def _parse_expressao_linha(self):
        token = self._current_token()
        if token:
            if token.type == "PLUS":
                self._match_token("PLUS")
                self._parse_termo()
                self._parse_expressao_linha()
            elif token.type == "MINUS":
                self._match_token("MINUS")
                self._parse_termo()
                self._parse_expressao_linha()

    def _parse_termo(self):
        self._parse_fator()
        self._parse_termo_linha()

    def _parse_termo_linha(self):
        token = self._current_token()
        if token:
            if token.type == "STAR":
                self._match_token("STAR")
                self._parse_fator()
                self._parse_termo_linha()
            elif token.type == "SLASH":
                self._match_token("SLASH")
                self._parse_fator()
                self._parse_termo_linha()

    def _parse_fator(self):
        if self._match_token("IDENTIFIER"): pass
        elif self._match_token("NUMBER"): pass
        elif self._match_token("LPAREN"):
            self._parse_expressao()
            if not self._match_token("RPAREN"): self._error("Esperado ')' após expressão em parênteses")
        else:
            self._error("Fator inválido: esperado identificador, número ou '('")

    def _parse_desvio(self):
        if not self._match_token("GO"): self._error("Esperado 'GO' para desvio")
        if not self._match_token("TO"): self._error("Esperado 'TO' após 'GO'")
        if not self._match_token("IDENTIFIER"): self._error("Esperado identificador (rótulo) após 'GO TO'")

    def _parse_leitura(self):
        if not self._match_token("READ"): self._error("Esperado 'READ'")
        self._parse_lista_de_identificadores()

    def _parse_lista_de_identificadores(self):
        token = self._current_token()
        if token and token.type == "IDENTIFIER":
            self._match_token("IDENTIFIER")
            while self._current_token() and self._current_token().type == "COMMA":
                self._match_token("COMMA")
                if not self._match_token("IDENTIFIER"):
                    self._error("Esperado identificador após vírgula na lista de leitura")

    def _parse_impressao(self):
        if not self._match_token("PRINT"): self._error("Esperado 'PRINT'")
        self._parse_lista_de_expressoes()

    def _parse_lista_de_expressoes(self):
        token = self._current_token()
        expr_start_tokens = {"IDENTIFIER", "NUMBER", "LPAREN"}

        if token and token.type in expr_start_tokens:
            self._parse_expressao()
            while self._current_token() and self._current_token().type == "COMMA":
                self._match_token("COMMA")
                next_token_for_expr = self._current_token()
                if not (next_token_for_expr and next_token_for_expr.type in expr_start_tokens):
                     self._error("Esperada expressão após vírgula na lista de impressão")
                self._parse_expressao()

    def _parse_decisao(self):
        if not self._match_token("IF"): self._error("Esperado 'IF'")
        self._parse_comparacao()
        if not self._match_token("THEN"): self._error("Esperado 'THEN' após comparação")

        if self._current_token() and self._current_token().type == "ELSE":
            self._error("Comando esperado após 'THEN' e antes de 'ELSE'")
        self._parse_comando()
        
        if not self._match_token("ELSE"): self._error("Esperado 'ELSE' após comando da cláusula 'THEN'")
        self._parse_comando()

    def _parse_comparacao(self):
        self._parse_expressao()
        op_token = self._current_token()
        if op_token and op_token.type in {"EQ", "GT", "LT"}:
            self._match_token(op_token.type)
        else:
            self._error("Esperado operador de comparação ('=', '>', '<')")
        self._parse_expressao()

if __name__ == "__main__":
    input_code = input("Digite o código: ")
    sfp = SingleFileParser()

    try:
        sfp.parse(input_code)
        print("Análise concluída com sucesso!")
    except LexerError as e:
        print(f"Erro Léxico: {e}")
        sys.exit(1)
    except ParseError as e:
        print(f"Erro Sintático: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)