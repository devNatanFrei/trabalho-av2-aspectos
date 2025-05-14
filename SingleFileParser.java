//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.
import java.util.ArrayList; // Importa a classe ArrayList para usar listas dinâmicas
import java.util.List;      // Importa a interface List para trabalhar com listas
import java.util.Set;       // Importa a interface Set para trabalhar com conjuntos (coleções sem duplicatas)
import java.util.regex.Matcher; // Importa a classe Matcher para encontrar correspondências em texto usando expressões regulares
import java.util.regex.Pattern; // Importa a classe Pattern para compilar expressões regulares
import java.util.Scanner;   // Importa a classe Scanner para ler entrada do usuário (do teclado)

public class SingleFileParser { // Declaração da classe principal que fará a análise léxica e sintática

    // --- Classe Token Interna ---
    // Representa um "token", que é a menor unidade significativa do código fonte.
    public static class Token {
        public final String type;  // O tipo do token (ex: "NUMBER", "IDENTIFIER", "LET")
        public final String value; // O valor real do token (ex: "123", "VARIAVELX", "LET")

        // Construtor da classe Token
        public Token(String type, String value) {
            this.type = type;   // Inicializa o tipo do token
            this.value = value; // Inicializa o valor do token
        }

        // Sobrescreve o método toString para fornecer uma representação em string amigável do token
        // Útil para depuração, para ver qual token foi gerado.
        @Override
        public String toString() {
            return "Token(" + type + ", '" + value + "')"; // Formato: Token(TIPO, 'VALOR')
        }
    }

    // --- Exceções Internas ---
    // Exceção personalizada para erros durante a análise léxica (criação de tokens).
    public static class LexerException extends Exception {
        // Construtor que recebe uma mensagem de erro.
        public LexerException(String message) {
            super(message); // Chama o construtor da classe pai (Exception) com a mensagem.
        }
    }

    // Exceção personalizada para erros durante a análise sintática (verificação da gramática).
    public static class ParseException extends Exception {
        // Construtor que recebe uma mensagem de erro.
        public ParseException(String message) {
            super(message); // Chama o construtor da classe pai (Exception) com a mensagem.
        }
    }

    // --- Especificações e Palavras-chave do Lexer ---
    // Classe interna auxiliar para definir cada tipo de token e sua expressão regular.
    private static class TokenSpec {
        String type;    // O tipo do token (ex: "NUMBER")
        Pattern pattern; // A expressão regular compilada para encontrar este tipo de token.

        // Construtor da TokenSpec.
        TokenSpec(String type, String regex) {
            this.type = type;   // Define o tipo do token.
            // Compila a expressão regular. O "^" no início garante que o padrão seja
            // procurado apenas no começo da string (ou substring) atual.
            // O "("+ regex +")" agrupa a regex para facilitar a extração do texto correspondente.
            this.pattern = Pattern.compile("^(" + regex + ")");
        }
    }

    // Lista para armazenar todas as especificações de tokens (regras do lexer).
    // É `final` porque a referência à lista não mudará, mas seu conteúdo sim.
    private final List<TokenSpec> tokenSpecs = new ArrayList<>();
    // Conjunto (`Set`) para armazenar as palavras-chave da linguagem.
    // Usar um `Set` é eficiente para verificar se uma string é uma palavra-chave.
    private final Set<String> keywords = Set.of(
            "LET", "GO", "TO", "READ", "PRINT", "IF", "THEN", "ELSE", "END"
    );

    // --- Estado do Parser ---
    private List<Token> tokens; // Lista para armazenar os tokens gerados pelo lexer.
    private int currentPos;     // Posição (índice) do token atual que o parser está analisando.


    // Construtor da classe SingleFileParser.
    // É chamado quando um objeto SingleFileParser é criado (ex: `new SingleFileParser()`).
    public SingleFileParser() {
        // Inicializa a lista `tokenSpecs` com as regras para cada tipo de token.
        // A ordem pode ser importante se houver ambiguidades, mas aqui está bem definida.
        tokenSpecs.add(new TokenSpec("NUMBER", "\\d+"));                    // Números (um ou mais dígitos)
        tokenSpecs.add(new TokenSpec("IDENTIFIER", "[A-Z][A-Z0-9]*"));      // Identificadores (começa com letra maiúscula, seguido por letras/números)
        tokenSpecs.add(new TokenSpec("ASSIGN", ":="));                      // Operador de atribuição
        tokenSpecs.add(new TokenSpec("PLUS", "\\+"));                       // Operador de soma (o '\' escapa o '+', que é especial em regex)
        tokenSpecs.add(new TokenSpec("MINUS", "-"));                        // Operador de subtração
        tokenSpecs.add(new TokenSpec("STAR", "\\*"));                       // Operador de multiplicação (o '\' escapa o '*')
        tokenSpecs.add(new TokenSpec("SLASH", "/"));                        // Operador de divisão
        tokenSpecs.add(new TokenSpec("EQ", "="));                           // Operador de igualdade
        tokenSpecs.add(new TokenSpec("GT", ">"));                           // Operador maior que
        tokenSpecs.add(new TokenSpec("LT", "<"));                           // Operador menor que
        tokenSpecs.add(new TokenSpec("LPAREN", "\\("));                     // Parêntese esquerdo (o '\' escapa o '(')
        tokenSpecs.add(new TokenSpec("RPAREN", "\\)"));                     // Parêntese direito (o '\' escapa o ')')
        tokenSpecs.add(new TokenSpec("SEMI", ";"));                         // Ponto e vírgula
        tokenSpecs.add(new TokenSpec("COLON", ":"));                        // Dois pontos
        tokenSpecs.add(new TokenSpec("COMMA", ","));                        // Vírgula
        tokenSpecs.add(new TokenSpec("WHITESPACE", "\\s+"));                // Espaço em branco (um ou mais espaços, tabs, novas linhas) - será ignorado
    }

    // --- Método do Lexer ---
    // Transforma a string de entrada (código fonte) em uma lista de Tokens.
    // Lança LexerException se encontrar um caractere inválido.
    public List<Token> tokenize(String input) throws LexerException {
        List<Token> generatedTokens = new ArrayList<>(); // Lista para guardar os tokens encontrados.
        int currentInputPos = 0; // Posição atual na string de entrada.
        int inputLength = input.length(); // Comprimento total da string de entrada.

        // Loop principal: continua enquanto não chegar ao fim da string de entrada.
        while (currentInputPos < inputLength) {
            boolean matched = false; // Flag para indicar se algum token foi encontrado nesta iteração.
            // Loop interno: tenta cada especificação de token (regra) da lista `tokenSpecs`.
            for (TokenSpec spec : tokenSpecs) {
                // Cria um Matcher para tentar encontrar o padrão da regra atual
                // a partir da posição `currentInputPos` da string de entrada.
                Matcher matcher = spec.pattern.matcher(input.substring(currentInputPos));
                // `matcher.find()` tenta encontrar o padrão no início da substring.
                if (matcher.find()) {
                    // Pega o texto que correspondeu ao padrão. `group(1)` pega o conteúdo do primeiro
                    // grupo de captura na regex (que é a regex inteira devido ao `(` e `)` em TokenSpec).
                    String text = matcher.group(1);

                    // Tratamento especial se o tipo da regra for "IDENTIFIER".
                    if (spec.type.equals("IDENTIFIER")) {
                        // Verifica se o texto identificado é uma palavra-chave.
                        if (keywords.contains(text)) {
                            // Se for uma palavra-chave, o tipo do token é a própria palavra-chave (ex: "LET").
                            generatedTokens.add(new Token(text, text));
                        } else {
                            // Caso contrário, é um identificador comum.
                            generatedTokens.add(new Token("IDENTIFIER", text));
                        }
                    } else if (!spec.type.equals("WHITESPACE")) {
                        // Se o tipo não for "WHITESPACE" (espaço em branco), adiciona o token à lista.
                        // Espaços em branco são efetivamente ignorados.
                        generatedTokens.add(new Token(spec.type, text));
                    }

                    currentInputPos += text.length(); // Avança a posição na string de entrada.
                    matched = true; // Marca que um token foi encontrado.
                    break; // Sai do loop interno (das TokenSpecs), pois um token foi encontrado.
                }
            }
            // Se, após tentar todas as regras, nenhum token foi encontrado (`matched` continua `false`).
            if (!matched) {
                // Lança uma exceção indicando um caractere inválido.
                throw new LexerException("Caractere inválido na posição " + currentInputPos + ": '" + input.charAt(currentInputPos) + "'");
            }
        }
        return generatedTokens; // Retorna a lista de tokens gerada.
    }

    // --- Métodos Auxiliares do Parser ---
    // Retorna o token atual (na posição `currentPos`) sem consumi-lo (avançar a posição).
    // É como "espiar" o próximo token.
    private Token currentToken() {
        if (currentPos < tokens.size()) { // Verifica se ainda há tokens na lista.
            return tokens.get(currentPos); // Retorna o token atual.
        }
        return null; // Retorna null se não houver mais tokens.
    }

    // Verifica se o token atual corresponde ao `expectedType`.
    // Se corresponder, consome o token (avança `currentPos`) e retorna `true`.
    // Caso contrário, retorna `false` e não consome o token.
    private boolean matchToken(String expectedType) {
        Token token = currentToken(); // Pega o token atual.
        // Verifica se há um token atual e se o tipo dele é o esperado.
        if (token != null && token.type.equals(expectedType)) {
            currentPos++; // Avança para o próximo token (consome o atual).
            return true;  // Retorna true indicando sucesso.
        }
        return false; // Retorna false indicando que não houve correspondência.
    }

    // Lança uma exceção de erro de parsing (ParseExceptio_n).
    // Inclui uma mensagem, informações sobre o token atual e a posição do erro.
    private void error(String message) throws ParseException {
        String tokenInfo = ""; // String para informações adicionais do token.
        if (currentToken() != null) { // Se houver um token atual.
            tokenInfo = " (próximo token: " + currentToken() + ")"; // Adiciona info do token atual.
        }
        // Lança a exceção com a mensagem formatada.
        throw new ParseException("Erro: " + message + tokenInfo + " na posição do token " + currentPos + ".");
    }


    // Método principal que orquestra a análise léxica e sintática.
    public void parse(String inputCode) throws LexerException, ParseException {
        this.tokens = tokenize(inputCode); // 1. Executa a análise léxica para obter a lista de tokens.
        this.currentPos = 0;               // 2. Reseta a posição do parser para o início da lista de tokens.

        parsePrograma();                   // 3. Inicia a análise sintática a partir da regra "programa".
    }

    // Método para analisar a regra <programa> ::= <sequência de comandos> END
    private void parsePrograma() throws ParseException {
        parseSequenciaDeComandos(); // Analisa a sequência de comandos.
        if (!matchToken("END")) {   // Verifica se o próximo token é "END".
            error("Esperado 'END' no final do programa"); // Se não for, lança erro.
        }
        if (currentToken() != null) { // Verifica se há tokens restantes após "END".
            error("Tokens extras após 'END'"); // Se houver, lança erro.
        }
    }

    // Método para analisar a regra <sequência de comandos> ::= <comando> <sequência de comandos linha>
    private void parseSequenciaDeComandos() throws ParseException {
        parseComando();                    // Analisa o primeiro comando.
        parseSequenciaDeComandosLinha();   // Analisa o restante da sequência (comandos separados por ';').
    }

    // Método para analisar <sequência de comandos linha> ::= ; <comando> <sequência de comandos linha> | e (epsilon/vazio)
    // Esta é uma forma de lidar com recursão à esquerda (comando ; comando ; comando...) de forma descendente.
    private void parseSequenciaDeComandosLinha() throws ParseException {
        Token token = currentToken(); // Pega o token atual.
        // Se o token atual for um ponto e vírgula (SEMI).
        if (token != null && token.type.equals("SEMI")) {
            matchToken("SEMI");                    // Consome o ';'.
            parseComando();                        // Espera e analisa outro comando.
            parseSequenciaDeComandosLinha();       // Chama recursivamente para mais comandos com ';'.
        }
        // Se não for ';', então é a produção vazia (epsilon), não faz nada e retorna.
    }

    // Método para analisar a regra <comando> (pode ser LET, GO, READ, PRINT, IF, rótulo ou vazio).
    private void parseComando() throws ParseException {
        Token token = currentToken(); // Pega o token atual.
        if (token == null) return; // Se não houver mais tokens, retorna (pode ser fim do programa ou erro pego depois).

        // Decide qual tipo de comando é baseado no tipo do token atual.
        if (token.type.equals("LET")) {
            parseAtribuicao(); // Se for "LET", analisa uma atribuição.
        } else if (token.type.equals("GO")) {
            parseDesvio();     // Se for "GO", analisa um desvio.
        } else if (token.type.equals("READ")) {
            parseLeitura();    // Se for "READ", analisa uma leitura.
        } else if (token.type.equals("PRINT")) {
            parseImpressao();  // Se for "PRINT", analisa uma impressão.
        } else if (token.type.equals("IF")) {
            parseDecisao();    // Se for "IF", analisa uma decisão.
        } else if (token.type.equals("IDENTIFIER") && // Se for um IDENTIFIER...
                currentPos + 1 < tokens.size() &&   // ...e houver um próximo token...
                tokens.get(currentPos + 1).type.equals("COLON")) { // ...e o próximo token for ":" (COLON).
            // Então é um rótulo (label).
            matchToken("IDENTIFIER"); // Consome o identificador do rótulo.
            matchToken("COLON");      // Consome os dois pontos.
            parseComando();           // Analisa o comando que segue o rótulo.
        } else if (Set.of("END", "ELSE", "THEN", "SEMI").contains(token.type)) {
            // Caso "epsilon" (comando vazio): Se o token atual for END, ELSE, THEN ou SEMI,
            // significa que um comando pode ter terminado ou ser opcional aqui.
            // O parser não faz nada, representando a produção vazia da gramática.
            // A lógica de erro (se um comando era OBRIGATÓRIO) é tratada pela função que chamou parseComando.
        } else {
            // Se não for nenhum dos comandos conhecidos nem um token de terminação/continuação,
            // o método `parseComando` retorna. Se um comando era esperado pela regra chamadora
            // (ex: após um ';'), a falha em encontrar um token esperado causará um erro lá.
            // Para esta gramática, um comando "inválido" aqui pode significar um erro de sintaxe
            // que será pego quando uma expectativa não for atendida mais acima na pilha de chamadas.
        }
    }

    // Método para analisar <atribuição> ::= LET <identificador> := <expressão>
    private void parseAtribuicao() throws ParseException {
        if (!matchToken("LET")) error("Esperado 'LET' para atribuição"); // Espera "LET".
        if (!matchToken("IDENTIFIER")) error("Esperado identificador após 'LET'"); // Espera um identificador.
        if (!matchToken("ASSIGN")) error("Esperado ':=' após identificador na atribuição"); // Espera ":=".
        parseExpressao(); // Analisa a expressão à direita da atribuição.
    }

    // Método para analisar <expressão> ::= <termo> <expressão linha>
    private void parseExpressao() throws ParseException {
        parseTermo();             // Analisa o primeiro termo.
        parseExpressaoLinha();    // Analisa o restante da expressão (+ termo, - termo, ou nada).
    }

    // Método para <expressão linha> ::= + <termo> <expressão linha> | - <termo> <expressão linha> | e
    private void parseExpressaoLinha() throws ParseException {
        Token token = currentToken(); // Pega o token atual.
        if (token != null) { // Se houver um token.
            if (token.type.equals("PLUS")) { // Se for '+'.
                matchToken("PLUS");        // Consome '+'.
                parseTermo();              // Analisa o próximo termo.
                parseExpressaoLinha();     // Chama recursivamente para mais adições/subtrações.
            } else if (token.type.equals("MINUS")) { // Se for '-'.
                matchToken("MINUS");       // Consome '-'.
                parseTermo();              // Analisa o próximo termo.
                parseExpressaoLinha();     // Chama recursivamente.
            }
            // Se não for '+' nem '-', é a produção vazia (epsilon), retorna.
        }
    }

    // Método para analisar <termo> ::= <fator> <termo linha>
    private void parseTermo() throws ParseException {
        parseFator();           // Analisa o primeiro fator.
        parseTermoLinha();      // Analisa o restante do termo (* fator, / fator, ou nada).
    }

    // Método para <termo linha> ::= * <fator> <termo linha> | / <fator> <termo linha> | e
    private void parseTermoLinha() throws ParseException {
        Token token = currentToken(); // Pega o token atual.
        if (token != null) { // Se houver um token.
            if (token.type.equals("STAR")) { // Se for '*'.
                matchToken("STAR");        // Consome '*'.
                parseFator();              // Analisa o próximo fator.
                parseTermoLinha();         // Chama recursivamente para mais multiplicações/divisões.
            } else if (token.type.equals("SLASH")) { // Se for '/'.
                matchToken("SLASH");       // Consome '/'.
                parseFator();              // Analisa o próximo fator.
                parseTermoLinha();         // Chama recursivamente.
            }
            // Se não for '*' nem '/', é a produção vazia (epsilon), retorna.
        }
    }

    // Método para analisar <fator> ::= <identificador> | <número> | ( <expressão> )
    private void parseFator() throws ParseException {
        if (matchToken("IDENTIFIER")) { /* Consumido com sucesso, não faz mais nada */ }
        else if (matchToken("NUMBER")) { /* Consumido com sucesso */ }
        else if (matchToken("LPAREN")) { // Se for '('.
            parseExpressao();             // Analisa a expressão dentro dos parênteses.
            if (!matchToken("RPAREN")) error("Esperado ')' após expressão em parênteses"); // Espera ')'.
        } else {
            // Se não for identificador, número ou '(', lança erro.
            error("Fator inválido: esperado identificador, número ou '('");
        }
    }

    // Método para analisar <desvio> ::= GO TO <rótulo>
    // (A forma GO TO <número> OF <lista de rótulos> não está implementada no parser).
    private void parseDesvio() throws ParseException {
        if (!matchToken("GO")) error("Esperado 'GO' para desvio"); // Espera "GO".
        if (!matchToken("TO")) error("Esperado 'TO' após 'GO'");   // Espera "TO".
        // Espera um identificador (que é o rótulo).
        if (!matchToken("IDENTIFIER")) error("Esperado identificador (rótulo) após 'GO TO'");
    }

    // Método para analisar <leitura> ::= READ <lista de identificadores>
    private void parseLeitura() throws ParseException {
        if (!matchToken("READ")) error("Esperado 'READ'"); // Espera "READ".
        parseListaDeIdentificadores(); // Analisa a lista de identificadores.
    }

    // Método para analisar <lista de identificadores> ::= <identificador> <lista cont.> | e
    // <lista cont.> ::= , <identificador> <lista cont.> | e
    private void parseListaDeIdentificadores() throws ParseException {
        Token token = currentToken(); // Pega o token atual.
        // Se o token atual for um IDENTIFIER (início da lista).
        if (token != null && token.type.equals("IDENTIFIER")) {
            matchToken("IDENTIFIER"); // Consome o primeiro identificador.
            // Loop para consumir mais identificadores separados por vírgula.
            while (currentToken() != null && currentToken().type.equals("COMMA")) {
                matchToken("COMMA"); // Consome a vírgula.
                // Após a vírgula, espera outro identificador.
                if (!matchToken("IDENTIFIER")) {
                    error("Esperado identificador após vírgula na lista de leitura");
                }
            }
        }
        // Se o primeiro token não for IDENTIFIER, é uma lista vazia (epsilon), o que é permitido.
    }

    // Método para analisar <impressão> ::= PRINT <lista de expressões>
    private void parseImpressao() throws ParseException {
        if (!matchToken("PRINT")) error("Esperado 'PRINT'"); // Espera "PRINT".
        parseListaDeExpressoes(); // Analisa a lista de expressões.
    }

    // Método para analisar <lista de expressões> ::= <expressão> <lista cont.> | e
    // <lista cont.> ::= , <expressão> <lista cont.> | e
    private void parseListaDeExpressoes() throws ParseException {
        Token token = currentToken(); // Pega o token atual.
        // Define quais tipos de token podem iniciar uma expressão.
        Set<String> exprStartTokens = Set.of("IDENTIFIER", "NUMBER", "LPAREN");

        // Se o token atual puder iniciar uma expressão.
        if (token != null && exprStartTokens.contains(token.type)) {
            parseExpressao(); // Analisa a primeira expressão.
            // Loop para consumir mais expressões separadas por vírgula.
            while (currentToken() != null && currentToken().type.equals("COMMA")) {
                matchToken("COMMA"); // Consome a vírgula.
                // Após a vírgula, verifica se o próximo token pode iniciar outra expressão.
                Token nextTokenForExpr = currentToken();
                if (nextTokenForExpr == null || !exprStartTokens.contains(nextTokenForExpr.type)) {
                     error("Esperada expressão após vírgula na lista de impressão");
                }
                parseExpressao(); // Analisa a próxima expressão.
            }
        }
        // Se o primeiro token não puder iniciar uma expressão, é uma lista vazia (epsilon).
    }

    // Método para analisar <decisão> ::= IF <comparação> THEN <comando> ELSE <comando>
    private void parseDecisao() throws ParseException {
        if (!matchToken("IF")) error("Esperado 'IF'"); // Espera "IF".
        parseComparacao(); // Analisa a condição de comparação.
        if (!matchToken("THEN")) error("Esperado 'THEN' após comparação"); // Espera "THEN".

        // VERIFICAÇÃO IMPORTANTE: Se o próximo token (após THEN) já for ELSE,
        // significa que o comando da cláusula THEN está ausente.
        if (currentToken() != null && currentToken().type.equals("ELSE")) {
            error("Comando esperado após 'THEN' e antes de 'ELSE'");
        }
        parseComando(); // Analisa o comando da cláusula THEN.
        
        if (!matchToken("ELSE")) error("Esperado 'ELSE' após comando da cláusula 'THEN'"); // Espera "ELSE".
        parseComando(); // Analisa o comando da cláusula ELSE.
    }

    // Método para analisar <comparação> ::= <expressão> <operador de comparação> <expressão>
    private void parseComparacao() throws ParseException {
        parseExpressao(); // Analisa a primeira expressão da comparação.
        Token opToken = currentToken(); // Pega o token atual (que deve ser o operador).
        // Verifica se o token é um dos operadores de comparação válidos.
        if (opToken != null && (opToken.type.equals("EQ") || opToken.type.equals("GT") || opToken.type.equals("LT"))) {
            matchToken(opToken.type); // Consome o operador.
        } else {
            error("Esperado operador de comparação ('=', '>', '<')"); // Se não for, lança erro.
        }
        parseExpressao(); // Analisa a segunda expressão da comparação.
    }


    // --- Método Main para Teste ---
    // Ponto de entrada do programa.
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in); // Cria um Scanner para ler entrada do console.
        System.out.println("Digite o código:"); // Pede ao usuário para digitar o código.
        String inputCode = scanner.nextLine(); // Lê a linha inteira de código digitada.

        SingleFileParser sfp = new SingleFileParser(); // Cria uma instância do nosso parser.

        try {
            sfp.parse(inputCode); // Tenta analisar o código fornecido.
            // Se `parse` não lançar exceção, a análise foi bem-sucedida.
            System.out.println("Análise concluída com sucesso!");

        } catch (LexerException e) { // Se ocorrer um erro léxico.
            System.err.println("Erro Léxico: " + e.getMessage()); // Imprime a mensagem de erro léxico.
        } catch (ParseException e) { // Se ocorrer um erro sintático.
            System.err.println("Erro Sintático: " + e.getMessage()); // Imprime a mensagem de erro sintático.
        } catch (Exception e) { // Captura qualquer outra exceção inesperada.
            System.err.println("Erro inesperado: " + e.getMessage());
            e.printStackTrace(); // Imprime o rastreamento da pilha da exceção para depuração.
        } finally {
            scanner.close(); // Garante que o Scanner seja fechado, liberando recursos do sistema.
        }
    }
}