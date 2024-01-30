matrix_size = 3
matrix = [[(i, (i + j) % matrix_size) for j in range(matrix_size)] for i in range(matrix_size)]

# Transpose the matrix to get the desired output
matrix = list(map(list, zip(*matrix)))

# Print the matrix
for row in matrix:
    print(row)
