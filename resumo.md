
Esse código representa um **analisador léxico e sintático** de uma linguagem de programação simplificada, com comandos como `LET`, `PRINT`, `IF`, `GO TO`, `READ`, `END` e labels.

### ✅ **Resumo do funcionamento:**

#### 1. **Lexer (Analisador Léxico)**
O método `tokenize()` percorre o código-fonte (string de entrada) e transforma caracteres em **tokens**:
- Palavras reservadas (`LET`, `IF`, `THEN`, etc.) são marcadas como `keyword`
- Identificadores (variáveis, labels) são `ide`
- Números inteiros são `num`
- Símbolos e operadores (`:=`, `+`, `-`, `(`, `)`, etc.) são `operator` ou `punctuation`

Erros como caracteres inválidos (ex: `VAR$`) causam erro léxico e interrompem a análise.

#### 2. **Parser (Analisador Sintático)**
O método `parse(String inputString)` realiza a **análise sintática** baseada em regras definidas pela gramática da linguagem:
- **Comandos válidos** são analisados por `command()`
- Sequências de comandos são analisadas por `commandSequence()`
- Expressões são analisadas por `expression()` e `factor()`
- Labels são verificados (inclusive duplicatas)
- Verifica presença obrigatória de `END` no final do programa

#### 3. **Erros detectados**
- **Léxicos**: Caracteres inválidos
- **Sintáticos**: Estrutura incorreta (ex: falta de `;`, `:=`, `END`, etc.)
- **Semânticos (limitados)**: Labels duplicados, `GO TO` com número fora da faixa

---

### ✅ **Exemplos de testes cobertos**
A função `main()` testa diferentes cenários:
- Entradas válidas
- Erros léxicos e sintáticos
- Casos limite e ambíguos