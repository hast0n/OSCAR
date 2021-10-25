# Helper for Kivy GUI

import numpy

def getColorMatrix(matrix, color_mapping):
    # new_matrix = [[0 for i in range(len(matrix[0]))] for j in range(len(matrix))]
    new_matrix = numpy.ndarray(shape=[len(matrix), len(matrix[0]), 3], dtype=numpy.uint8)
    xlen, ylen, span = new_matrix.shape
    for i in range(xlen) :
        for j in range(ylen):
            cell = matrix[i][j]
            cell = cell.type if cell else 'empty'
            new_matrix[i,j] = color_mapping[cell]
    return new_matrix