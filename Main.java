import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class Main {
    public static void main(String[] args) {
        LexerParser lexerParser = new LexerParser();

        System.out.println("--- Testes Originais ---");
        lexerParser.parse("L1: LET A := 1; L1: PRINT A; END");
        lexerParser.parse("GO TO 0 OF L1, L2; L1: PRINT 1; L2: PRINT 2; END");
        lexerParser.parse("LET A := 5; PRINT A; END");

        System.out.println("\n--- A. Entradas Válidas ---");
        lexerParser.parse("END");
        lexerParser.parse("LET X := 10; PRINT X + 5; END");
        lexerParser.parse("READ VAL; IF VAL > 0 THEN PRINT VAL ELSE PRINT 0 - VAL; END");
        lexerParser.parse("L1: READ A, B; GO TO L1; END");
        lexerParser.parse("GO TO 2 OF LABEL1, LABEL2, LABEL3; LABEL1: PRINT 1; LABEL2: PRINT 2; LABEL3: PRINT 3; END");
        lexerParser.parse("LET RESULT := (A + B) * (C - D / 2); PRINT RESULT; END");
        lexerParser.parse("START: IF X = Y THEN LET Z := 1 ELSE LET Z := 0; PRINT Z; END");
        lexerParser.parse("PRINT A,B,C; END");
        lexerParser.parse("IF A <= B THEN PRINT A ELSE PRINT B; END");
        lexerParser.parse("L: LET A := 1; IF A = 1 THEN PRINT A ELSE PRINT B; END");

        System.out.println("\n--- B. Erros Léxicos ---");
        lexerParser.parse("LET VAR$ := 10; END");

        System.out.println("\n--- C. Erros Sintáticos (Estruturais) ---");
        lexerParser.parse("LET X = 10; END");
        lexerParser.parse("IF A > B THEN PRINT A END");
        lexerParser.parse("PRINT A B; END");
        lexerParser.parse("READ X, ; END");
        lexerParser.parse("GO TO ; END");
        lexerParser.parse("LET A := 1 PRINT B := 2; END");
        lexerParser.parse("LET A := (1 + 2; END");
        lexerParser.parse("L1: LET X := 10; GO TO OF L2; END");
        lexerParser.parse("LET A := 1; LET B := 2");
        lexerParser.parse("PRINT A+; END");
        lexerParser.parse("IF A > B THEN ; ELSE PRINT B; END");
        lexerParser.parse("IF A > B THEN PRINT A ELSE ; END");
        lexerParser.parse("L1: ; END");

        System.out.println("\n--- D. Erros Semânticos (Lógica detectada pelo parser) ---");
        lexerParser.parse("GO TO 3 OF L1, L2; L1: PRINT 1; L2: PRINT 2; END");
        lexerParser.parse("LBL: PRINT 1; LBL: PRINT 2; END");

        System.out.println("\n--- E. Casos Limites e Específicos ---");
        lexerParser.parse("LET A := 1;; END");
        lexerParser.parse("READ ; END");
        lexerParser.parse("IF A < B THEN GO TO L1 ELSE GO TO L2; L1: PRINT A; L2: PRINT B; END EXTRA_TOKEN");
        lexerParser.parse("GO TO 1 OF LBL; LBL: PRINT \"OK\"; END");
        lexerParser.parse("");
        lexerParser.parse("LET A:=1;END");
        lexerParser.parse("   LET    A  :=  1 ;  PRINT   A  ;  END   ");
        lexerParser.parse("GO TO 1 OF ; END");
        lexerParser.parse("GO TO 1 OF L1, ; END");

        System.out.println("\n--- Testes Adicionais de Lógica ---");
        lexerParser.parse("IF X THEN PRINT Y ELSE PRINT Z; END");
        lexerParser.parse("LET A := B C; END");
        lexerParser.parse("L1: READ X Y; END");
        lexerParser.parse("PRINT ,A; END");
        lexerParser.parse("PRINT A,; END");
    }
}

class LexerParser {

    public static class Token {
        public final String category;
        public final String value;

        public Token(String category, String value) {
            this.category = category;
            this.value = value;
        }

        @Override
        public String toString() {
            return "Token(" + category + ", '" + value + "')";
        }
    }

    private static final Set<String> RESERVED_WORDS = new HashSet<>(Arrays.asList(
            "END", "LET", "GO", "TO", "OF", "READ", "PRINT", "IF", "THEN", "ELSE"
    ));
    private String currentInputString;
    private int lexerIndex;

    private List<Token> tokens;
    private int parserPosition;
    private Set<String> labelsDefined;
    private boolean errorFound;

    public LexerParser() {
        this.labelsDefined = new HashSet<>();
    }

    private boolean tokenize() {
        this.tokens = new ArrayList<>();
        this.lexerIndex = 0;

        while (lexerIndex < currentInputString.length()) {
            char currentChar = currentInputString.charAt(lexerIndex);

            if (Character.isWhitespace(currentChar)) {
                lexerIndex++;
                continue;
            }

            if (Character.isLetter(currentChar)) {
                StringBuilder wordBuilder = new StringBuilder();
                while (lexerIndex < currentInputString.length() && Character.isLetterOrDigit(currentInputString.charAt(lexerIndex))) {
                    wordBuilder.append(currentInputString.charAt(lexerIndex));
                    lexerIndex++;
                }
                String word = wordBuilder.toString();
                if (RESERVED_WORDS.contains(word.toUpperCase())) {
                    tokens.add(new Token("keyword", word.toUpperCase()));
                } else {
                    tokens.add(new Token("ide", word));
                }
                continue;
            }

            if (Character.isDigit(currentChar)) {
                StringBuilder numberBuilder = new StringBuilder();
                while (lexerIndex < currentInputString.length() && Character.isDigit(currentInputString.charAt(lexerIndex))) {
                    numberBuilder.append(currentInputString.charAt(lexerIndex));
                    lexerIndex++;
                }
                tokens.add(new Token("num", numberBuilder.toString()));
                continue;
            }

            if (currentChar == ':') {
                if (lexerIndex + 1 < currentInputString.length() && currentInputString.charAt(lexerIndex + 1) == '=') {
                    tokens.add(new Token("operator", ":="));
                    lexerIndex += 2;
                } else {
                    tokens.add(new Token("punctuation", ":"));
                    lexerIndex++;
                }
                continue;
            }

            if (currentChar == '>') {
                if (lexerIndex + 1 < currentInputString.length() && currentInputString.charAt(lexerIndex + 1) == '=') {
                    tokens.add(new Token("operator", ">="));
                    lexerIndex += 2;
                } else {
                    tokens.add(new Token("operator", ">"));
                    lexerIndex++;
                }
                continue;
            }

            if (currentChar == '<') {
                if (lexerIndex + 1 < currentInputString.length() && currentInputString.charAt(lexerIndex + 1) == '=') {
                    tokens.add(new Token("operator", "<="));
                    lexerIndex += 2;
                } else {
                    tokens.add(new Token("operator", "<"));
                    lexerIndex++;
                }
                continue;
            }
            
            if (currentChar == '=' || currentChar == '+' || currentChar == '-' || currentChar == '*' || currentChar == '/') {
                 tokens.add(new Token("operator", String.valueOf(currentChar)));
                 lexerIndex++;
                 continue;
            }

            if (currentChar == ';' || currentChar == ',' || currentChar == '(' || currentChar == ')') {
                tokens.add(new Token("punctuation", String.valueOf(currentChar)));
                lexerIndex++;
                continue;
            }

            System.err.println("Erro Léxico: Caractere inválido '" + currentChar + "' na posição " + lexerIndex);
            this.errorFound = true;
            return false;
        }
        return true;
    }

    private void reportError(String message) {
        if (!errorFound) {
            System.err.println("Erro Sintático: " + message + (parserPosition < tokens.size() ? " próximo ao token " + tokens.get(parserPosition) : " no final da entrada."));
        }
        errorFound = true;
    }

    private Token currentToken() {
        if (parserPosition < tokens.size()) {
            return tokens.get(parserPosition);
        }
        return null;
    }

    private Token consumeToken() {
        if (parserPosition < tokens.size()) {
            return tokens.get(parserPosition++);
        }
        return null;
    }
    
    private boolean matchAndConsume(String category, String value) {
        Token current = currentToken();
        if (current != null && current.category.equals(category) && current.value.equals(value)) {
            consumeToken();
            return true;
        }
        return false;
    }

    private boolean matchCategoryAndConsume(String category) {
        Token current = currentToken();
        if (current != null && current.category.equals(category)) {
            consumeToken();
            return true;
        }
        return false;
    }

    private void factor() {
        if (errorFound || currentToken() == null) return;
        Token current = currentToken();
        if ("ide".equals(current.category) || "num".equals(current.category)) {
            consumeToken();
        } else if (matchAndConsume("punctuation", "(")) {
            expression();
            if (!matchAndConsume("punctuation", ")")) {
                reportError("Esperado ')' após a expressão no fator.");
            }
        } else {
            reportError("Esperado identificador, número ou '(' para um fator.");
        }
    }

    private void expression() {
        if (errorFound || currentToken() == null) return;
        factor();
        while (!errorFound && currentToken() != null && "operator".equals(currentToken().category) &&
               Arrays.asList("+", "-", "*", "/").contains(currentToken().value)) {
            consumeToken();
            factor();
        }
    }
    
    private void commandSequence() {
        while (!errorFound && currentToken() != null &&
               !("keyword".equals(currentToken().category) && "END".equals(currentToken().value))) {
            command();
            if (errorFound) break;
            Token current = currentToken();
            if (current != null && "punctuation".equals(current.category) && ";".equals(current.value)) {
                consumeToken();
                if (currentToken() == null || ("keyword".equals(currentToken().category) && "END".equals(currentToken().value))) {
                    break; 
                }
            } else if (current != null && !("keyword".equals(current.category) && "END".equals(current.value))) {
                reportError("Esperado ';' ou 'END' após um comando.");
                break;
            } else {
                break;
            }
        }
    }

    private void command() {
        if (errorFound || currentToken() == null) return;
        Token current = currentToken();

        if ("ide".equals(current.category) && 
            parserPosition + 1 < tokens.size() && 
            "punctuation".equals(tokens.get(parserPosition + 1).category) &&
            ":".equals(tokens.get(parserPosition + 1).value)) {
            String label = current.value;
            if (labelsDefined.contains(label)) {
                reportError("Definição duplicada de rótulo '" + label + "'.");
                return;
            }
            labelsDefined.add(label);
            consumeToken(); 
            consumeToken(); 
            command(); 
            return;
        }

        if (!"keyword".equals(current.category)) {
            reportError("Esperada uma palavra-chave para um comando ou uma definição de rótulo.");
            return;
        }

        String keywordValue = current.value;
        consumeToken(); 

        switch (keywordValue) {
            case "LET":
                if (!matchCategoryAndConsume("ide")) {
                    reportError("Esperado identificador após 'LET'."); return;
                }
                if (!matchAndConsume("operator", ":=")) {
                    reportError("Esperado ':=' após o identificador na instrução 'LET'."); return;
                }
                expression();
                break;

            case "GO":
                if (!matchAndConsume("keyword", "TO")) {
                    reportError("Esperado 'TO' após 'GO'."); return;
                }
                Token target = currentToken();
                if (target == null) {
                    reportError("Esperado identificador ou número após 'GO TO'."); return;
                }

                if ("ide".equals(target.category)) {
                    consumeToken();
                } else if ("num".equals(target.category)) {
                    String numStr = target.value;
                    consumeToken();
                    if (!matchAndConsume("keyword", "OF")) {
                        reportError("Esperado 'OF' após o número na instrução 'GO TO ... OF ...'."); return;
                    }
                    
                    List<String> labelList = new ArrayList<>();
                    Token firstLabelToken = currentToken();
                    if (firstLabelToken == null || !"ide".equals(firstLabelToken.category)) {
                        reportError("Esperado pelo menos um identificador na lista de rótulos após 'OF'."); return;
                    }
                    labelList.add(firstLabelToken.value);
                    consumeToken();

                    while (matchAndConsume("punctuation", ",")) {
                        Token nextLabelToken = currentToken();
                        if (nextLabelToken == null || !"ide".equals(nextLabelToken.category)) {
                            reportError("Esperado identificador após ',' na lista de rótulos."); return;
                        }
                        labelList.add(nextLabelToken.value);
                        consumeToken(); 
                    }
                    try {
                        int numVal = Integer.parseInt(numStr);
                        if (numVal < 1 || numVal > labelList.size()) {
                            reportError("Número " + numVal + " em 'GO TO' está fora dos limites para a lista de rótulos de tamanho " + labelList.size() + ".");
                        }
                    } catch (NumberFormatException e) {
                        reportError("Formato de número inválido '" + numStr + "' na instrução 'GO TO'.");
                    }

                } else {
                    reportError("Esperado identificador ou número após 'GO TO'.");
                }
                break;

            case "READ":
                Token firstReadVar = currentToken();
                if (firstReadVar == null || !"ide".equals(firstReadVar.category)) {
                    reportError("Esperado pelo menos um identificador após 'READ'."); return;
                }
                consumeToken();
                while (matchAndConsume("punctuation", ",")) {
                    Token nextReadVar = currentToken();
                    if (nextReadVar == null || !"ide".equals(nextReadVar.category)) {
                        reportError("Esperado identificador após ',' na lista 'READ'."); return;
                    }
                    consumeToken();
                }
                break;

            case "PRINT":
                expression();
                if (errorFound) return;
                while (matchAndConsume("punctuation", ",")) {
                    expression();
                    if (errorFound) return;
                }
                break;

            case "IF":
                expression();
                if (errorFound) return;
                Token relOp = currentToken();
                if (relOp == null || !"operator".equals(relOp.category) ||
                    !Arrays.asList("=", ">", ">=", "<", "<=").contains(relOp.value)) {
                    reportError("Esperado operador relacional (por exemplo, '=', '>', '<=', etc.) após a primeira expressão em 'IF'."); return;
                }
                consumeToken(); 
                expression();
                if (errorFound) return;
                if (!matchAndConsume("keyword", "THEN")) {
                    reportError("Esperado 'THEN' após a condição na instrução 'IF'."); return;
                }
                command(); 
                if (errorFound) return;
                
                Token checkElse = currentToken();
                if (checkElse != null && "keyword".equals(checkElse.category) && "ELSE".equals(checkElse.value)) {
                    consumeToken();
                    command(); 
                } else {
                     reportError("Esperado 'ELSE' após o comando 'THEN'.");
                }
                break;
            
            case "END":
                reportError("Palavra-chave 'END' inesperada. 'END' deve terminar o programa.");
                parserPosition--; 
                break;

            default:
                reportError("Palavra-chave não reconhecida '" + keywordValue + "' para um comando.");
                break;
        }
    }

    public void parse(String inputString) {
        this.currentInputString = inputString;
        this.tokens = null; 
        this.parserPosition = 0;
        this.labelsDefined.clear();
        this.errorFound = false;
        this.lexerIndex = 0;

        System.out.println("\nAnalisando: \"" + inputString + "\"");

        if (!tokenize()) {
            System.err.println("Análise léxica falhou. Análise sintática abortada.");
            return;
        }
        
        if (this.tokens.isEmpty() && !this.currentInputString.trim().isEmpty() && !this.errorFound) {
             System.err.println("Análise léxica retornou nenhum token para entrada não vazia (por exemplo, apenas caracteres inválidos). Análise sintática abortada.");
             return;
        }

        if (tokens.isEmpty()) {
            reportError("Esperado 'END' para um programa vazio, mas encontrado entrada vazia.");
            System.out.println("Análise sintática falhou devido a erros.");
            return;
        }

        if (tokens.size() == 1 && "keyword".equals(tokens.get(0).category) && "END".equals(tokens.get(0).value)) {
            System.out.println("Análise sintática bem-sucedida.");
            return;
        }
        
        commandSequence();

        if (!errorFound) {
            Token current = currentToken();
            if (current != null && "keyword".equals(current.category) && "END".equals(current.value)) {
                consumeToken();
                if (currentToken() == null) {
                    System.out.println("Análise sintática bem-sucedida.");
                } else {
                    reportError("Tokens extras encontrados após 'END'. Próximo token: " + currentToken());
                    System.out.println("Análise sintática falhou devido a erros.");
                }
            } else {
                if (current == null && !errorFound) {
                     reportError("Esperado 'END' no final do programa.");
                } else if (!errorFound) {
                     reportError("Esperado 'END' ou estrutura de comando inválida próximo a '" + (current != null ? current.value : "EOF") + "'.");
                }
                 System.out.println("Análise sintática falhou devido a erros.");
            }
        } else {
            System.out.println("Análise sintática falhou devido a erro(s) relatado(s) acima.");
        }
    }
}