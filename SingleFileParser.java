import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.Scanner;

public class SingleFileParser {

    // --- Classe Token Interna ---
    public static class Token {
        public final String type;
        public final String value;

        public Token(String type, String value) {
            this.type = type;
            this.value = value;
        }

        @Override
        public String toString() {
            return "Token(" + type + ", '" + value + "')";
        }
    }

    // --- Exceções Internas ---
    public static class LexerException extends Exception {
        public LexerException(String message) {
            super(message);
        }
    }

    public static class ParseException extends Exception {
        public ParseException(String message) {
            super(message);
        }
    }

    // --- Especificações e Palavras-chave do Lexer ---
    private static class TokenSpec {
        String type;
        Pattern pattern;

        TokenSpec(String type, String regex) {
            this.type = type;
            this.pattern = Pattern.compile("^(" + regex + ")");
        }
    }

    private final List<TokenSpec> tokenSpecs = new ArrayList<>();
    private final Set<String> keywords = Set.of(
        "LET", "GO", "TO", "READ", "PRINT", "IF", "THEN", "ELSE", "END"
    );

    // --- Estado do Parser ---
    private List<Token> tokens;
    private int currentPos;


    public SingleFileParser() {
     
        tokenSpecs.add(new TokenSpec("NUMBER", "\\d+"));
        tokenSpecs.add(new TokenSpec("IDENTIFIER", "[A-Z][A-Z0-9]*"));
        tokenSpecs.add(new TokenSpec("ASSIGN", ":="));
        tokenSpecs.add(new TokenSpec("PLUS", "\\+"));
        tokenSpecs.add(new TokenSpec("MINUS", "-"));
        tokenSpecs.add(new TokenSpec("STAR", "\\*"));
        tokenSpecs.add(new TokenSpec("SLASH", "/"));
        tokenSpecs.add(new TokenSpec("EQ", "="));
        tokenSpecs.add(new TokenSpec("GT", ">"));
        tokenSpecs.add(new TokenSpec("LT", "<"));
        tokenSpecs.add(new TokenSpec("LPAREN", "\\("));
        tokenSpecs.add(new TokenSpec("RPAREN", "\\)"));
        tokenSpecs.add(new TokenSpec("SEMI", ";"));
        tokenSpecs.add(new TokenSpec("COLON", ":"));
        tokenSpecs.add(new TokenSpec("COMMA", ","));
        tokenSpecs.add(new TokenSpec("WHITESPACE", "\\s+"));
    }

    // --- Método do Lexer ---
    public List<Token> tokenize(String input) throws LexerException {
        List<Token> generatedTokens = new ArrayList<>();
        int currentInputPos = 0;
        int inputLength = input.length();

        while (currentInputPos < inputLength) {
            boolean matched = false;
            for (TokenSpec spec : tokenSpecs) {
                Matcher matcher = spec.pattern.matcher(input.substring(currentInputPos));
                if (matcher.find()) {
                    String text = matcher.group(1);
                    
                    if (spec.type.equals("IDENTIFIER")) {
                        if (keywords.contains(text)) {
                            generatedTokens.add(new Token(text, text));
                        } else {
                            generatedTokens.add(new Token("IDENTIFIER", text));
                        }
                    } else if (!spec.type.equals("WHITESPACE")) {
                        generatedTokens.add(new Token(spec.type, text));
                    }
                    
                    currentInputPos += text.length();
                    matched = true;
                    break; 
                }
            }
            if (!matched) {
                throw new LexerException("Caractere inválido na posição " + currentInputPos + ": '" + input.charAt(currentInputPos) + "'");
            }
        }
        return generatedTokens;
    }

    // --- Métodos Auxiliares do Parser ---
    private Token currentToken() {
        if (currentPos < tokens.size()) {
            return tokens.get(currentPos);
        }
        return null;
    }

    private boolean matchToken(String expectedType) {
        Token token = currentToken();
        if (token != null && token.type.equals(expectedType)) {
            currentPos++;
            return true;
        }
        return false;
    }

    private void error(String message) throws ParseException {
        String tokenInfo = "";
        if (currentToken() != null) {
            tokenInfo = " (próximo token: " + currentToken() + ")";
        }
        throw new ParseException("Erro: " + message + tokenInfo + " na posição do token " + currentPos + ".");
    }

  

    public void parse(String inputCode) throws LexerException, ParseException {
        this.tokens = tokenize(inputCode); 
        this.currentPos = 0;               
        
     
        
        parsePrograma(); 
    }

    private void parsePrograma() throws ParseException {
        parseSequenciaDeComandos();
        if (!matchToken("END")) {
            error("Esperado 'END' no final do programa");
        }
        if (currentToken() != null) {
            error("Tokens extras após 'END'");
        }
    }

    private void parseSequenciaDeComandos() throws ParseException {
        parseComando();
        parseSequenciaDeComandosLinha();
    }

    private void parseSequenciaDeComandosLinha() throws ParseException {
        Token token = currentToken();
        if (token != null && token.type.equals("SEMI")) {
            matchToken("SEMI");
            parseComando();
            parseSequenciaDeComandosLinha();
        }
    }

    private void parseComando() throws ParseException {
        Token token = currentToken();
        if (token == null) return;

        if (token.type.equals("LET")) {
            parseAtribuicao();
        } else if (token.type.equals("GO")) {
            parseDesvio();
        } else if (token.type.equals("READ")) {
            parseLeitura();
        } else if (token.type.equals("PRINT")) {
            parseImpressao();
        } else if (token.type.equals("IF")) {
            parseDecisao();
        } else if (token.type.equals("IDENTIFIER") &&
                   currentPos + 1 < tokens.size() &&
                   tokens.get(currentPos + 1).type.equals("COLON")) {
            matchToken("IDENTIFIER");
            matchToken("COLON");
            parseComando();
        } else if (Set.of("END", "ELSE", "THEN", "SEMI").contains(token.type)) {
           
        } else {
     
        }
    }

    private void parseAtribuicao() throws ParseException {
        if (!matchToken("LET")) error("Esperado 'LET' para atribuição");
        if (!matchToken("IDENTIFIER")) error("Esperado identificador após 'LET'");
        if (!matchToken("ASSIGN")) error("Esperado ':=' após identificador na atribuição");
        parseExpressao();
    }

    private void parseExpressao() throws ParseException {
        parseTermo();
        parseExpressaoLinha();
    }

    private void parseExpressaoLinha() throws ParseException {
        Token token = currentToken();
        if (token != null) {
            if (token.type.equals("PLUS")) {
                matchToken("PLUS");
                parseTermo();
                parseExpressaoLinha();
            } else if (token.type.equals("MINUS")) {
                matchToken("MINUS");
                parseTermo();
                parseExpressaoLinha();
            }
        }
    }

    private void parseTermo() throws ParseException {
        parseFator();
        parseTermoLinha();
    }

    private void parseTermoLinha() throws ParseException {
        Token token = currentToken();
        if (token != null) {
            if (token.type.equals("STAR")) {
                matchToken("STAR");
                parseFator();
                parseTermoLinha();
            } else if (token.type.equals("SLASH")) {
                matchToken("SLASH");
                parseFator();
                parseTermoLinha();
            }
        }
    }

    private void parseFator() throws ParseException {
        if (matchToken("IDENTIFIER")) { /* ok */ }
        else if (matchToken("NUMBER")) { /* ok */ }
        else if (matchToken("LPAREN")) {
            parseExpressao();
            if (!matchToken("RPAREN")) error("Esperado ')' após expressão em parênteses");
        } else {
            error("Fator inválido: esperado identificador, número ou '('");
        }
    }

    private void parseDesvio() throws ParseException {
        if (!matchToken("GO")) error("Esperado 'GO' para desvio");
        if (!matchToken("TO")) error("Esperado 'TO' após 'GO'");
        if (!matchToken("IDENTIFIER")) error("Esperado identificador (rótulo) após 'GO TO'");
    }

    private void parseLeitura() throws ParseException {
        if (!matchToken("READ")) error("Esperado 'READ'");
        parseListaDeIdentificadores();
    }

    private void parseListaDeIdentificadores() throws ParseException {
        Token token = currentToken();
        if (token != null && token.type.equals("IDENTIFIER")) {
            matchToken("IDENTIFIER");
            while (currentToken() != null && currentToken().type.equals("COMMA")) {
                matchToken("COMMA");
                if (!matchToken("IDENTIFIER")) {
                    error("Esperado identificador após vírgula na lista de leitura");
                }
            }
        }
    }

    private void parseImpressao() throws ParseException {
        if (!matchToken("PRINT")) error("Esperado 'PRINT'");
        parseListaDeExpressoes();
    }

    private void parseListaDeExpressoes() throws ParseException {
        Token token = currentToken();
        Set<String> exprStartTokens = Set.of("IDENTIFIER", "NUMBER", "LPAREN");

        if (token != null && exprStartTokens.contains(token.type)) {
            parseExpressao();
            while (currentToken() != null && currentToken().type.equals("COMMA")) {
                matchToken("COMMA");
                Token nextTokenForExpr = currentToken();
                if (nextTokenForExpr == null || !exprStartTokens.contains(nextTokenForExpr.type)) {
                     error("Esperada expressão após vírgula na lista de impressão");
                }
                parseExpressao();
            }
        }
    }

    private void parseDecisao() throws ParseException {
        if (!matchToken("IF")) error("Esperado 'IF'");
        parseComparacao();
        if (!matchToken("THEN")) error("Esperado 'THEN' após comparação");

        if (currentToken() != null && currentToken().type.equals("ELSE")) {
            error("Comando esperado após 'THEN' e antes de 'ELSE'");
        }
        parseComando();
        
        if (!matchToken("ELSE")) error("Esperado 'ELSE' após comando da cláusula 'THEN'");
        parseComando();
    }

    private void parseComparacao() throws ParseException {
        parseExpressao();
        Token opToken = currentToken();
        if (opToken != null && (opToken.type.equals("EQ") || opToken.type.equals("GT") || opToken.type.equals("LT"))) {
            matchToken(opToken.type);
        } else {
            error("Esperado operador de comparação ('=', '>', '<')");
        }
        parseExpressao();
    }


    // --- Método Main para Teste ---
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.println("Digite o código:");
        String inputCode = scanner.nextLine(); 

        SingleFileParser sfp = new SingleFileParser();

        try {
            sfp.parse(inputCode);
            System.out.println("Análise concluída com sucesso!");

        } catch (LexerException e) {
            System.err.println("Erro Léxico: " + e.getMessage());
        } catch (ParseException e) {
            System.err.println("Erro Sintático: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("Erro inesperado: " + e.getMessage());
            e.printStackTrace();
        } finally {
            scanner.close();
        }
    }
}