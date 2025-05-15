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
        tokens = []
        pos = 0
        while pos < len(codigo_entrada):
            matched = False
            for tipo, padrao in self.especificacoes_token:
                regex = re.compile(padrao)
                match = regex.match(codigo_entrada, pos)
                if match:
                    texto = match.group(0)
                    if tipo == "IDENTIFICADOR" and texto in self.palavras_chave:
                        tokens.append(Token(texto, texto))
                    elif tipo != "ESPACO_BRANCO":
                        tokens.append(Token(tipo, texto))
                    pos = match.end()
                    matched = True
                    break
            if not matched:
                raise ErroLexico(f"Caractere inválido na posição {pos}: '{codigo_entrada[pos]}'")
        return tokens

    def analisar(self, codigo_entrada):
        self.tokens = self._tokenizar(codigo_entrada)
        self.posicao_atual = 0
        self._programa()
        if self._peek():
            raise ErroSintatico("Tokens extras após o final do programa")
        print("Análise concluída com sucesso!")

    def _peek(self):
        return self.tokens[self.posicao_atual] if self.posicao_atual < len(self.tokens) else None

    def _eat(self, tipo):
        if self._peek() and self._peek().tipo == tipo:
            tok = self._peek()
            self.posicao_atual += 1
            return tok
        return None

    def _expect(self, tipo):
        tok = self._eat(tipo)
        if not tok:
            raise ErroSintatico(f"Esperado token {tipo}, mas obteve {self._peek()}")
        return tok

    
    def _programa(self):
        self._sequencia_de_comandos()
        self._expect("END")  

   
    def _sequencia_de_comandos(self):
        self._envoltura_comando()
        while self._eat("PONTO_VIRGULA"):
            if self._peek() and self._peek().tipo == "END":
                raise ErroSintatico("Ponto e vírgula antes de END não permitido")
            self._envoltura_comando()

 
    def _envoltura_comando(self):
        if self._peek() and self._peek().tipo == "IDENTIFICADOR" and self.tokens[self.posicao_atual+1].tipo == "DOIS_PONTOS":
            self._eat("IDENTIFICADOR")
            self._eat("DOIS_PONTOS")
        self._comando()


    def _comando(self):
        tok = self._peek()
        if not tok:
            raise ErroSintatico("Comando esperado, mas fim inesperado")
        if tok.tipo == "LET":
            self._eat("LET"); self._eat("IDENTIFICADOR"); self._eat("ATRIBUICAO_OP"); self._expressao()
        elif tok.tipo == "GO":
            self._eat("GO"); self._eat("TO"); self._eat("IDENTIFICADOR");
            if self._eat("OF"): self._lista_de_rotulos()
        elif tok.tipo == "READ":
            self._eat("READ"); self._lista_de_identificadores()
        elif tok.tipo == "PRINT":
            self._eat("PRINT"); self._lista_de_expressoes()
        elif tok.tipo == "IF":
            self._eat("IF"); self._comparacao(); self._eat("THEN"); self._envoltura_comando(); self._eat("ELSE"); self._envoltura_comando()
        elif tok.tipo in {"END", "ELSE", "PONTO_VIRGULA"}:
            return
        else:
            raise ErroSintatico(f"Token inesperado {tok}")


    def _expressao(self):
        self._termo()
        while self._peek() and self._peek().tipo in {"MAIS","MENOS"}:
            self._eat(self._peek().tipo)
            self._termo()


    def _termo(self):
        self._fator()
        while self._peek() and self._peek().tipo in {"ASTERISCO","BARRA"}:
            self._eat(self._peek().tipo)
            self._fator()


    def _fator(self):
        if self._eat("IDENTIFICADOR"):
            return
        if self._eat("NUMERO"):
            return
        if self._eat("PARENTESE_ESQ"):
            self._expressao(); self._eat("PARENTESE_DIR"); return
        if self._eat("END"):
            return
        raise ErroSintatico(f"Fator inválido: {self._peek()}")


    def _lista_de_rotulos(self):
        self._eat("IDENTIFICADOR")
        while self._eat("VIRGULA"): self._eat("IDENTIFICADOR")

   
    def _lista_de_identificadores(self):
        if self._peek() and self._peek().tipo == "IDENTIFICADOR":
            self._eat("IDENTIFICADOR")
            while self._eat("VIRGULA"): self._eat("IDENTIFICADOR")

    
    def _lista_de_expressoes(self):
        if self._peek() and self._peek().tipo in {"IDENTIFICADOR","NUMERO","PARENTESE_ESQ","END"}:
            self._expressao()
            while self._eat("VIRGULA"): self._expressao()

 
    def _comparacao(self):
        self._expressao()
        if not self._eat("IGUAL") and not self._eat("MAIOR_QUE") and not self._eat("MENOR_QUE"):
            raise ErroSintatico(f"Operador de comparação esperado: {self._peek()}")
        self._expressao()

if __name__ == "__main__":
    codigo = input("Digite o código: ")
    analisador = AnalisadorSintaticoArquivoUnico()
    try:
        analisador.analisar(codigo)
    except Exception as e:
        print(e)
        sys.exit(1)
