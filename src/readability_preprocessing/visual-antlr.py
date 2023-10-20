# import antlr4
#
# from src.antlr.JavaLexer import JavaLexer
#
# # TODO: Use Javalang vs ANTLR4 vs Pygments
#
# # Sample Java code
# java_code = """
# // This is a comment
# int num = 42;
# String text = "Hello, World!";
# """
#
# # Create an input stream
# input_stream = antlr4.InputStream(java_code)
#
# # Create the lexer
# lexer = JavaLexer(input_stream)
#
# # Tokenize the code
# tokens = antlr4.CommonTokenStream(lexer)
# tokens.fill()
#
# # Define a mapping of token types to categories
# category_mapping = {
#     JavaLexer.WS: 'Whitespace',
#     JavaLexer.COMMENT: 'Comment',
#     JavaLexer.LINE_COMMENT: 'Comment',
#     JavaLexer.STRING_LITERAL: 'Literal',
#     JavaLexer.CHAR_LITERAL: 'Literal',
#     JavaLexer.BOOL_LITERAL: 'Literal',
#     JavaLexer.DECIMAL_LITERAL: 'Literal',
#     JavaLexer.HEX_LITERAL: 'Literal',
#     JavaLexer.OCT_LITERAL: 'Literal',
#     JavaLexer.NULL_LITERAL: 'Literal',
#     JavaLexer.LONG: 'Type',
#     JavaLexer.INT: 'Type',
#     JavaLexer.FLOAT: 'Type',
#     JavaLexer.DOUBLE: 'Type',
#     JavaLexer.BOOLEAN: 'Type',
#     JavaLexer.VOID: 'Type',
#     JavaLexer.NEW: 'Keyword',
#     JavaLexer.PUBLIC: 'Keyword',
#     JavaLexer.PRIVATE: 'Keyword',
#     JavaLexer.PROTECTED: 'Keyword',
#     JavaLexer.STATIC: 'Keyword',
#     JavaLexer.FINAL: 'Keyword',
#     # Add more mappings based on your requirements
# }
#
# # Iterate through the tokens and categorize them
# categorized_tokens = []
# for token in tokens.tokens:
#     token_type = token.type
#     token_text = token.text
#     category = category_mapping.get(token_type, 'Other')
#
#     categorized_tokens.append((token_text, category))
#
# # Display the categorized tokens
# for token_text, category in categorized_tokens:
#     print(f'Token: {token_text}, Category: {category}')
