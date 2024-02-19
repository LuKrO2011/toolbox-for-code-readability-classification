/**
 * The main method is the entry point of the program.
 *
 * @param args Command-line arguments (not used in this program).
 */
public static void main(String[] args) {
    // This line prints the string "Hello, World!" to the console.
    System.out.println("Hello, World!"); // Display greeting

    // You can also use the println method to print an empty line.
    System.out.println(); // Display an empty line

    // Variables can be used to store and manipulate data.
    String greeting = "Welcome to Java!"; // This is a String variable.
    System.out.println(greeting); // Display the value of the 'greeting' variable

    // Concatenation is combining strings using the + operator.
    System.out.println("The message is: " + greeting); // Display concatenated string

    // Escape sequences are special characters preceded by a backslash.
    System.out.println("This is a new line.\nThis is another line."); // Display multiple lines

    // Comments are ignored by the compiler and are for human readability.
    // Single-line comments start with double slashes.

    /*
     * Multi-line comments use delimiters.
     * They can span multiple lines.
     */

    // Java is case-sensitive, so be careful with capitalization.
    // System.out.println("hello, world!"); // This would be a different statement.

    // Always remember to end statements with a semicolon (;).

    // Comments within 'strings provide explanations for specific lines of code.
    String commentExample = "// 'This is a comment within a string.";
    System.out.println(commentExample);
}
