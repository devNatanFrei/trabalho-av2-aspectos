import re
import sys

class Token:
    def __init__(self, tipo, valor):
        self.tipo = tipo
        self.valor = valor

    def __repr__(self):
        return f"Token({self.tipo}, '{self.valor}')"

class ErroLexico(Exception):
    pass

class ErroSintatico(Exception):
    pass

class AnalisadorSintaticoArquivoUnico:
    def __init__(self):
        self.especificacoes_token = [
            ("NUMERO", r'\d+'),
            ("IDENTIFICADOR", r'[A-Z][A-Z0-9]*'),
            ("ATRIBUICAO_OP", r':='),
            ("MAIS", r'\+'),
            ("MENOS", r'-'),
            ("ASTERISCO", r'\*'),
            ("BARRA", r'/'),
            ("IGUAL", r'='),
            ("MAIOR_QUE", r'>'),
            ("MENOR_QUE", r'<'),
            ("PARENTESE_ESQ", r'\('),
            ("PARENTESE_DIR", r'\)'),
            ("PONTO_VIRGULA", r';'),
            ("DOIS_PONTOS", r':'),
            ("VIRGULA", r','),
            ("ESPACO_BRANCO", r'\s+'),
        ]
        self.palavras_chave = {"LET", "GO", "TO", "OF", "READ", "PRINT", "IF", "THEN", "ELSE", "END"}
        self.tokens = []
        self.posicao_atual = 0

    def _tokenizar(self, codigo_entrada):
        tokens_gerados = []
        posicao_entrada_atual = 0
        tamanho_entrada = len(codigo_entrada)

        while posicao_entrada_atual < tamanho_entrada:
            combinou = False
            for tipo_token, padrao_str in self.especificacoes_token:
                padrao = re.compile(padrao_str)
                match = padrao.match(codigo_entrada, posicao_entrada_atual)
                if match:
                    texto = match.group(0)
                    if tipo_token == "IDENTIFICADOR":
                        if texto in self.palavras_chave:
                            tokens_gerados.append(Token(texto, texto))
                        else:
                            tokens_gerados.append(Token("IDENTIFICADOR", texto))
                    elif tipo_token != "ESPACO_BRANCO":
                        tokens_gerados.append(Token(tipo_token, texto))

                    posicao_entrada_atual = match.end(0)
                    combinou = True
                    break
            if not combinou:
                raise ErroLexico(
                    f"Caractere inválido na posição {posicao_entrada_atual}: '{codigo_entrada[posicao_entrada_atual]}'")
        return tokens_gerados

    def _token_atual(self):
        if self.posicao_atual < len(self.tokens):
            return self.tokens[self.posicao_atual]
        return None

    def _espiar_token(self, deslocamento=1):
        posicao_espiar = self.posicao_atual + deslocamento
        if posicao_espiar < len(self.tokens):
            return self.tokens[posicao_espiar]
        return None

    def _combinar_token(self, tipo_esperado):
        token = self._token_atual()
        if token and token.tipo == tipo_esperado:
            self.posicao_atual += 1
            return token
        return None

    def _esperar_token(self, tipo_esperado, sufixo_mensagem_erro=""):
        token = self._combinar_token(tipo_esperado)
        if not token:
            self._erro(f"Esperado token '{tipo_esperado}'{sufixo_mensagem_erro}")
        return token

    def _erro(self, mensagem):
        info_token = ""
        if self._token_atual():
            info_token = f" (próximo token: {self._token_atual()})"
        raise ErroSintatico(f"Erro: {mensagem}{info_token} na posição do token {self.posicao_atual}.")

    def analisar(self, codigo_entrada):
        self.tokens = self._tokenizar(codigo_entrada)
        self.posicao_atual = 0
        self._analisar_programa()
        if self._token_atual() is not None:
             self._erro("Tokens extras após o final do programa")

    def _analisar_programa(self):
        self._analisar_sequencia_de_comandos()
        self._esperar_token("END", " no final do programa")

    def _analisar_sequencia_de_comandos(self):
        self._analisar_invólucro_comando()
        while self._token_atual() and self._token_atual().tipo == "PONTO_VIRGULA":
            self._combinar_token("PONTO_VIRGULA")
            if self._token_atual() and self._token_atual().tipo == "END":
                self._erro("Ponto e vírgula antes de 'END' não é permitido; comando esperado.")
            self._analisar_invólucro_comando()

    def _analisar_invólucro_comando(self):
        token = self._token_atual()
        proximo_token = self._espiar_token()
        if token and token.tipo == "IDENTIFICADOR" and proximo_token and proximo_token.tipo == "DOIS_PONTOS":
            self._analisar_rotulo()
            self._esperar_token("DOIS_PONTOS", " após o rótulo")
        self._analisar_comando()

    def _analisar_comando(self):
        token = self._token_atual()
        if not token:
            if not self._token_atual():
                self._erro("Comando esperado, mas o programa terminou inesperadamente.")
            return

        if token.tipo == "LET":
            self._analisar_atribuicao()
        elif token.tipo == "GO":
            self._analisar_desvio()
        elif token.tipo == "READ":
            self._analisar_leitura()
        elif token.tipo == "PRINT":
            self._analisar_impressao()
        elif token.tipo == "IF":
            self._analisar_decisao()
        elif token.tipo in {"END", "ELSE", "PONTO_VIRGULA"}:
            pass
        else:
            self._erro(f"Comando inválido ou token inesperado '{token.valor}' iniciando um comando.")

    def _analisar_atribuicao(self):
        self._esperar_token("LET")
        self._esperar_token("IDENTIFICADOR", " para nome da variável em atribuição")
        self._esperar_token("ATRIBUICAO_OP", " em atribuição")
        self._analisar_expressao()

    def _analisar_expressao(self):
        self._analisar_termo()
        while self._token_atual() and self._token_atual().tipo in {"MAIS", "MENOS"}:
            self._combinar_token(self._token_atual().tipo)
            self._analisar_termo()

    def _analisar_termo(self):
        self._analisar_fator()
        while self._token_atual() and self._token_atual().tipo in {"ASTERISCO", "BARRA"}:
            self._combinar_token(self._token_atual().tipo)
            self._analisar_fator()

    def _analisar_fator(self):
        if self._combinar_token("IDENTIFICADOR"):
            pass
        elif self._combinar_token("NUMERO"):
            pass
        elif self._combinar_token("PARENTESE_ESQ"):
            self._analisar_expressao()
            self._esperar_token("PARENTESE_DIR", " para fechar parênteses da expressão")
        else:
            self._erro("Fator inválido: esperado identificador, número ou expressão entre parênteses")

    def _analisar_desvio(self):
        self._esperar_token("GO")
        self._esperar_token("TO")
        self._esperar_token("IDENTIFICADOR", " para rótulo ou identificador de desvio")
        if self._combinar_token("OF"):
            self._analisar_lista_de_rotulos()

    def _analisar_lista_de_rotulos(self):
        self._analisar_rotulo()
        while self._combinar_token("VIRGULA"):
            self._analisar_rotulo()

    def _analisar_rotulo(self):
        self._esperar_token("IDENTIFICADOR", " para nome do rótulo")

    def _analisar_leitura(self):
        self._esperar_token("READ")
        self._analisar_lista_de_identificadores()

    def _analisar_lista_de_identificadores(self):
        token_atual = self._token_atual()
        if not (token_atual and token_atual.tipo == "IDENTIFICADOR"):
            return
        self._esperar_token("IDENTIFICADOR", " na lista de leitura ou lista vazia")
        while self._token_atual() and self._token_atual().tipo == "VIRGULA":
            self._combinar_token("VIRGULA")
            self._esperar_token("IDENTIFICADOR", " após vírgula na lista de leitura")

    def _analisar_impressao(self):
        self._esperar_token("PRINT")
        self._analisar_lista_de_expressoes()

    def _analisar_lista_de_expressoes(self):
        tokens_inicio_expr = {"IDENTIFICADOR", "NUMERO", "PARENTESE_ESQ"}
        token_atual = self._token_atual()
        if not (token_atual and token_atual.tipo in tokens_inicio_expr):
            return
        self._analisar_expressao()
        while self._token_atual() and self._token_atual().tipo == "VIRGULA":
            self._combinar_token("VIRGULA")
            proximo_token_para_expr = self._token_atual()
            if not (proximo_token_para_expr and proximo_token_para_expr.tipo in tokens_inicio_expr):
                self._erro("Esperada expressão após vírgula na lista de impressão")
            self._analisar_expressao()

    def _analisar_decisao(self):
        self._esperar_token("IF")
        self._analisar_comparacao()
        self._esperar_token("THEN", " após condição IF")
        self._analisar_invólucro_comando()
        self._esperar_token("ELSE", " após comando da cláusula 'THEN'")
        self._analisar_invólucro_comando()

    def _analisar_comparacao(self):
        self._analisar_expressao()
        self._analisar_operador_de_comparacao()
        self._analisar_expressao()

    def _analisar_operador_de_comparacao(self):
        token = self._token_atual()
        if token and token.tipo in {"IGUAL", "MAIOR_QUE", "MENOR_QUE"}:
            self._combinar_token(token.tipo)
        else:
            self._erro("Esperado operador de comparação ('=', '>', '<')")

if __name__ == "__main__":
    codigo_entrada = input("Digite o código: ")
    analisador = AnalisadorSintaticoArquivoUnico()
    try:
        analisador.analisar(codigo_entrada)
        print("Análise concluída com sucesso!")
    except ErroLexico as e:
        print(f"Erro Léxico: {e}")
        sys.exit(1)
    except ErroSintatico as e:
        print(f"Erro Sintático: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)