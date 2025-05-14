import java.util.*;

// Classe para representar um token
class Token {
    public String category;
    public String value;

    public Token(String category, String value) {
        this.category = category;
        this.value = value;
    }

    @Override
    public String toString() {
        return String.format("Token(%s, '%s')", category, value);
    }
}

public class BasicParser {
    // Lista de palavras-chave da linguagem
    private static final Set<String> RESERVED_WORDS = new HashSet<>(Arrays.asList(
        "END", "LET", "GO", "TO", "OF", "READ", "PRINT", "IF", "THEN", "ELSE"
    ));

    private List<Token> tokens;
    private int position;
    private Set<String> labelsDefined;
    private boolean errorFound;

    public BasicParser() {
        this.tokens = new ArrayList<>();
        this.position = 0;
        this.labelsDefined = new HashSet<>();
        this.errorFound = false;
    }

    // Função do analisador léxico
    private List<Token> tokenize(String input) {
        List<Token> tokenList = new ArrayList<>();
        int index = 0;
        while (index < input.length()) {
            char ch = input.charAt(index);
            if (Character.isWhitespace(ch)) {
                index++;
            } else if (Character.isLetter(ch)) {
                StringBuilder sb = new StringBuilder();
                while (index < input.length() && Character.isLetterOrDigit(input.charAt(index))) {
                    sb.append(input.charAt(index++));
                }
                String word = sb.toString();
                if (RESERVED_WORDS.contains(word.toUpperCase())) {
                    tokenList.add(new Token("keyword", word.toUpperCase()));
                } else {
                    tokenList.add(new Token("ide", word));
                }
            } else if (Character.isDigit(ch)) {
                StringBuilder sb = new StringBuilder();
                while (index < input.length() && Character.isDigit(input.charAt(index))) {
                    sb.append(input.charAt(index++));
                }
                tokenList.add(new Token("num", sb.toString()));
            } else {
                switch (ch) {
                    case ':' -> {
                        if (index + 1 < input.length() && input.charAt(index + 1) == '=') {
                            tokenList.add(new Token("operator", ":="));
                            index += 2;
                        } else {
                            tokenList.add(new Token("punctuation", ":"));
                            index++;
                        }
                    }
                    case '>' -> {
                        if (index + 1 < input.length() && input.charAt(index + 1) == '=') {
                            tokenList.add(new Token("operator", ">="));
                            index += 2;
                        } else {
                            tokenList.add(new Token("operator", ">"));
                            index++;
                        }
                    }
                    case '<' -> {
                        if (index + 1 < input.length() && input.charAt(index + 1) == '=') {
                            tokenList.add(new Token("operator", "<="));
                            index += 2;
                        } else {
                            tokenList.add(new Token("operator", "<"));
                            index++;
                        }
                    }
                    case '=', '+', '-', '*', '/' -> {
                        tokenList.add(new Token("operator", String.valueOf(ch)));
                        index++;
                    }
                    case ';', ',', '(', ')' -> {
                        tokenList.add(new Token("punctuation", String.valueOf(ch)));
                        index++;
                    }
                    default -> {
                        System.out.println("Erro: caractere inválido '" + ch + "'");
                        return null;
                    }
                }
            }
        }
        return tokenList;
    }

    // Funções do parser
    private void expression() {
        if (errorFound || position >= tokens.size()) return;
        factor();
        while (position < tokens.size() && "+-*/".contains(tokens.get(position).value)) {
            position++;
            factor();
        }
    }

    private void factor() {
        if (errorFound || position >= tokens.size()) return;
        Token cur = tokens.get(position);
        if (cur.category.equals("ide") || cur.category.equals("num")) {
            position++;
        } else if (cur.category.equals("punctuation") && cur.value.equals("(")) {
            position++;
            expression();
            if (position < tokens.size() && tokens.get(position).value.equals(")")) {
                position++;
            } else {
                System.out.println("Erro: esperado ')'");
                errorFound = true;
            }
        } else {
            System.out.println("Erro: esperado identificador, número ou '('");
            errorFound = true;
        }
    }

    private void commandSequence() {
        while (position < tokens.size() && !errorFound &&
              !(tokens.get(position).category.equals("keyword") && tokens.get(position).value.equals("END"))) {
            command();
            if (errorFound) break;
            if (position < tokens.size() && tokens.get(position).category.equals("punctuation") && tokens.get(position).value.equals(";")) {
                position++;
            } else {
                break;
            }
        }
    }

    private void command() {
        if (errorFound || position >= tokens.size()) return;
        Token cur = tokens.get(position);
        if (cur.category.equals("keyword")) {
            switch (cur.value) {
                case "LET" -> handleLet();
                case "GO"  -> handleGo();
                case "READ"-> handleRead();
                case "PRINT"-> handlePrint();
                case "IF"   -> handleIf();
                case "END"  -> {} // terminator handled elsewhere
            }
        } else if (cur.category.equals("ide") && position+1 < tokens.size()
                   && tokens.get(position+1).category.equals("punctuation")
                   && tokens.get(position+1).value.equals(""))) {
            // rótulo:ide:
        } else {
            System.out.println("Erro: comando inválido ou token inesperado '" + cur.value + "'");
            errorFound = true;
        }
    }

    // Implementar handleLet, handleGo, handleRead, handlePrint, handleIf conforme lógica Python
    // ... (omitted por brevidade)

    public void parse(String input) {
        System.out.println("\nAnalisando: \"" + input + "\"");
        tokens = tokenize(input);
        if (tokens == null) {
            System.out.println("Erro na análise léxica. Análise sintática abortada.");
            return;
        }
        position = 0;
        labelsDefined.clear();
        errorFound = false;

        if (tokens.isEmpty()) {
            System.out.println("Erro na análise sintática: entrada vazia, esperado 'END'");
            return;
        }
        if (tokens.size() == 1 && tokens.get(0).value.equals("END")) {
            System.out.println("Análise sintática bem-sucedida");
            return;
        }

        commandSequence();
        if (!errorFound && position < tokens.size()
            && tokens.get(position).category.equals("keyword")
            && tokens.get(position).value.equals("END")) {
            position++;
            if (position == tokens.size()) {
                System.out.println("Análise sintática bem-sucedida");
            } else {
                System.out.println("Erro na análise sintática: tokens extras após 'END'");
            }
        } else if (!errorFound) {
            System.out.println("Erro na análise sintática: esperado 'END' no final do programa");
        }
    }

    public static void main(String[] args) {
        BasicParser parser = new BasicParser();
        parser.parse("LET A := 1; PRINT A; END");
        parser.parse("END");
        // Adicione mais testes conforme desejado
    }
}
