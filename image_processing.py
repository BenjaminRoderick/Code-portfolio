#Benjamin Roderick
'''
takes as input a PGM "image" matrix, and allows the user to make multiple manipulations, such as:
	1.compressing
	2.cropping
	3.inverting
	4.flipping horizontaly or vertically
	5.saving and loading PGM files
'''


digits = ['0','1','2','3','4','5','6','7','8','9']

def deep_copy(image_matrix):
    '''
    (int[]) -> int[]
    
    Returns a deep copy of an input matrix.
    
    >>>deep_copy([[0,0,0,0,0],[1,1,1,1,1],[1,1,1,1,1]])
    [[0,0,0,0,0],[1,1,1,1,1],[1,1,1,1,1]]
    
    >>>deep_copy([[0,255],[255,0]])
    [[0,255],[255,0]]
    
    >>>deep_copy([[255,255,255],[0,0,0]])
    [[255,255,255],[0,0,0]]
    '''
    sublist = []
    
    copy_image = []
    
    for i in image_matrix:
        for n in i:
            sublist.append(n)
            
        copy_image.append(sublist)
        sublist = []
        
    return copy_image

def is_valid_image(image_matrix):
    '''
    (int[]) -> bool
    
    checks if an input matrix is a valid PGM image matrix. returns a bool
    
    >>>is_valid_image([[0,255,0],[0,1,5]])
    True
    
    >>>is_valid_image([['a','b'],[0,0]])
    False
    
    >>>is_valid_image([[-13,0],[255,1]])
    False
    '''
    found_error = False
    
    firstline = len(image_matrix[0])
    
    for i in range(len(image_matrix)):
        if len(image_matrix[i]) != firstline:
            found_error = True
            
            break
        
        for n in image_matrix[i]:
            if (type(n) != int) or (n > 255) or (n < 0):
                found_error = True
                
                break
            
        if found_error:
            break
            
    return (not found_error)

def is_valid_compressed_image(image_matrix):
    '''
    (str[]) -> bool
    
    Takes as an input a nested list of strings, returns a bool indicating whether or not it's a valid compressed PGM image.
    
    >>>is_valid_compressed_image([[0x5],[1x3,255x2],[130x5]])
    True
    
    >>>is_valid_compressed_image([[2,3,1],[4,7,1]])
    False
    
    >>>is_valid_compressed_image([[255x3],[-2x1,0x2]])
    False
    '''
    found_error = False
    
    B_sum = 0
    
    for i in range(len(image_matrix)):
        for n in image_matrix[i]:
            if (type(n) != str) or (n.count("x") != 1):
                found_error = True                
                break
            
            compareAB = n.split("x")
            
            A = compareAB[0]
            
            B = compareAB[1]
            
            if (A[0] in digits) and (B[0] in digits):
                A = int(A)
                B = int(B)
            else:
                found_error = True
                break
            
            if (A > 255) or (A < 0) or (B < 0):
                found_error = True
                break
            
            B_sum += B
            
        if i == 0:
            firstSum = B_sum
            
        if B_sum != firstSum:
            found_error = True
            break
            
        if found_error:
            break
        
        B_sum = 0
            
    return (not found_error)

def load_regular_image(filename):
    '''
    (str) -> int[]
    
    Takes as input a file name string, and returns a PGM image matrix.
    
    >>>fobj = open("test1.pgm", "w")
    >>>fobj.write("P2\\n2 2\\n255\\n0 0\\n255 0")
    20
    >>>fobj.close()
    >>>load_regular_image("test1.pgm")
    [[0, 0], [255, 0]]
    
    >>>fobj = open("test2.pgm", "w")
    >>>fobj.write("P2\\n3 2\\n255\\n0 30 0\\n255 0 100")
    27
    >>>fobj.close()
    >>>load_regular_image("test2.pgm")
    [[0,30,0],[255,0,100]]
    
    >>>fobj = open("test3.pgm", "w")
    >>>fobj.write("P2\\n3 3\\n255\\n255 0 10\\n200 0 60\\n0 0 0")
    34
    >>>fobj.close()
    >>>load_regular_image("test3.pgm")
    [[255, 0, 10], [200, 0, 60], [0, 0, 0]]
    '''
    fileobj = open(filename, "r")
    
    matrix = []
    
    for line in fileobj:
        matrix.append(line)
    
    fileobj.close()

    for i in range(len(matrix)):
        matrix[i] = matrix[i].split()
    
    if (matrix[0] != ["P2"]) or (len(matrix[1]) != 2) or (matrix[2] != ["255"]):
        raise AssertionError("Not a PGM image")
    
    image_matrix = matrix[3:]
    
    for i in range(len(image_matrix)):
        for n in range(len(image_matrix[i])):
            image_matrix[i][n] = int(image_matrix[i][n])
            
    if is_valid_image(image_matrix):  
        return image_matrix
    else:
        raise AssertionError("Not a PGM image")
    
def load_compressed_image(filename):
    '''
    (str) -> str[]
    
    Takes as input a file name string, and returns a compressed PGM image nested string.
    
    >>>fobj = open("test1.pgm.compressed", "w")
    >>>fobj.write("P2C\\n2 2\\n255\\n0x2\\n255x1 0x1")
    25
    >>>fobj.close()
    >>>load_compressed_image("test1.pgm.compressed")
    [["0x2"], ["255x1", "0x1"]]
    
    >>>fobj = open("test2.pgm.compressed", "w")
    >>>fobj.write("P2C\\n3 2\\n255\\n0x1 30x1 0\\n255 0 100")
    32
    >>>fobj.close()
    >>>load_compressed_image("test2.pgm.compressed")
    [["0x1","30x1","0x1"],["255x1","0x1","100x1"]]
    
    >>>fobj = open("test3.pgm.compressed", "w")
    >>>fobj.write("P2C\\n3 3\\n255\\n255x1 0x1 10x1\\n200x1 0x1 60x1\\n0x3")
    45
    >>>fobj.close()
    >>>load_compressed_image("test3.pgm.compressed")
    [["255x1", "0x1", "10x1"], ["200x1", "0x1", "60x1"], ["0x3"]]
    '''
    fileobj = open(filename, "r")
    
    matrix = []
    
    for line in fileobj:
        matrix.append(line)
    
    fileobj.close()

    for i in range(len(matrix)):
        matrix[i] = matrix[i].split()
        
    if (matrix[0] != ["P2C"]) or (len(matrix[1]) != 2) or (matrix[2] != ["255"]):
        raise AssertionError("Not a compressed PGM image")
        
    image_matrix = matrix[3:]
    
    if is_valid_compressed_image(image_matrix):
        return image_matrix
    else:
        raise AssertionError("Not a compressed PGM image")
    
    
def load_image(filename):
    '''
    (str) -> []
    
    Takes as input a file name string, and returns a PGM image matrix or a compressed PGM image nested string.

    >>>fobj = open("test1.pgm.compressed", "w")
    >>>fobj.write("P2C\\n2 2\\n255\\n0x2\\n255x1 0x1")
    25
    >>>fobj.close()
    >>>load_image("test1.pgm.compressed")
    [["0x2"], ["255x1", "0x1"]]
    
    >>>fobj = open("test2.pgm", "w")
    >>>fobj.write("P2\\n3 2\\n255\\n0 30 0\\n255 0 100")
    27
    >>>fobj.close()
    >>>load_image("test2.pgm")
    [[0,30,0],[255,0,100]]
    
    >>>fobj = open("test3.pgm.compressed", "w")
    >>>fobj.write("P2C\\n3 3\\n255\\n255x1 0x1 10x1\\n200x1 0x1 60x1\\n0x3")
    45
    >>>fobj.close()
    >>>load_image("test3.pgm.compressed")
    [["255x1", "0x1", "10x1"], ["200x1", "0x1", "60x1"], ["0x3"]]
    '''
    fileobj = open(filename, "r")
    
    firstline = fileobj.read(3)
    
    fileobj.close()
    
    if firstline == "P2\n":
        return load_regular_image(filename)
    
    elif firstline == "P2C":
        return load_compressed_image(filename)
    
    else:
        raise AssertionError("Not any type of PGM image")
    
    
def save_regular_image(image_matrix, filename):
    '''
    (int[], str) -> NoneType
    
    Takes as input a PGM image matrix and a filename string, saves the matrix as a PGM image file.
    
    >>>save_regular_image([[0, 0], [255, 0]], "test1.pgm")
    >>>fobj = open("test1.pgm", "r")
    >>>fobj.read()
    "P2\\n2 2\\n255\\n0 0\\n255 0"
    >>>fobj.close()
    
    >>>save_regular_image([[0,30,0],[255,0,100]], "test2.pgm")
    >>>fobj = open("test2.pgm", "r")
    >>>fobj.read()
    "P2\\n3 2\\n255\\n0 30 0\\n255 0 100"
    >>>fobj.close()
    
    >>>save_regular_image([[255, 0, 10], [200, 0, 60], [0, 0, 0]], "test3.pgm")
    >>>fobj = open("test3.pgm", "r")
    >>>fobj.read()
    "P2\\n3 3\\n255\\n255 0 10\\n200 0 60\\n0 0 0"
    >>>fobj.close()
    '''
    if not is_valid_image(image_matrix):
        raise AssertionError("Not a valid PGM image matrix")
    
    placeholder = ""
    
    fileobj = open(filename, "w")
    
    fileobj.write("P2\n")
    
    fileobj.write(str(len(image_matrix[0])) + " " + str(len(image_matrix)) + "\n")
    
    fileobj.write("255\n")
    
    for i in image_matrix:
        for n in i:
            placeholder += str(n) + " "
        
        placeholder = placeholder.strip()
        
        fileobj.write(placeholder + "\n")
        
        placeholder = ""
        
    fileobj.close()
    
        
def save_compressed_image(image_matrix, filename):
    '''
    (str[], str) -> NoneType
    
    Takes as input a compressed PGM image nested list and a filename string, saves the nested list as a compressed PGM image file.
    
    >>>save_compressed_image([["0x2"], ["255x1", "0x1"]], "test1.pgm.compressed")
    >>>fobj = open("test1.pgm.compressed", "r")
    >>>fobj.read()
    "P2C\\n2 2\\n255\\n0x2\\n255x1 0x1"
    >>>fobj.close()
    
    >>>save_compressed_image([["0x1","30x1","0x1"],["255x1","0x1","100x1"]], "test2.pgm.compressed")
    >>>fobj = open("test2.pgm.compressed", "r")
    >>>fobj.read()
    "P2C\\n3 2\\n255\\n0x1 30x1 0\\n255 0 100"
    >>>fobj.close()
    
    >>>save_compressed_image([["255x1", "0x1", "10x1"], ["200x1", "0x1", "60x1"], ["0x3"]], "test3.pgm.compressed")
    >>>fobj = open("test3.pgm.compressed", "r")
    >>>fobj.read()
    "P2C\\n3 3\\n255\\n255x1 0x1 10x1\\n200x1 0x1 60x1\\n0x3"
    >>>fobj.close()
    '''
    if not is_valid_compressed_image(image_matrix):
        raise AssertionError("Not a valid compressed PGM image matrix")
    
    placeholder = ""
    
    fileobj = open(filename, "w")
    
    fileobj.write("P2C\n")
    
    firstline = 0
    
    for i in image_matrix[0]:
        split = i.split("x")
        
        firstline += int(split[1])
    
    fileobj.write(str(firstline) + " " + str(len(image_matrix)) + "\n")
    
    fileobj.write("255\n")
    
    for i in image_matrix:
        for n in i:
            placeholder += n + " "
        
        placeholder = placeholder.strip()
        
        fileobj.write(placeholder + "\n")
        
        placeholder = ""
        
    fileobj.close()
    
def save_image(image_matrix, filename):
    '''
    ([], str) -> NoneType
    
    Takes as input a PGM image matrix and a filename string, saves the matrix as a PGM image file.
    Or takes as input a compressed PGM image nested list and a filename string, saves the nested list as a compressed PGM image file.
    
    >>>save_image([[0, 0], [255, 0]], "test1.pgm")
    >>>fobj = open("test1.pgm", "r")
    >>>fobj.read()
    "P2\\n2 2\\n255\\n0 0\\n255 0"
    >>>fobj.close()
    
    >>>save_image([["0x1","30x1","0x1"],["255x1","0x1","100x1"]], "test2.pgm.compressed")
    >>>fobj = open("test2.pgm.compressed", "r")
    >>>fobj.read()
    "P2C\\n3 2\\n255\\n0x1 30x1 0\\n255 0 100"
    >>>fobj.close()
    
    >>>save_image([[255, 0, 10], [200, 0, 60], [0, 0, 0]], "test3.pgm")
    >>>fobj = open("test3.pgm", "r")
    >>>fobj.read()
    "P2\\n3 3\\n255\\n255 0 10\\n200 0 60\\n0 0 0"
    >>>fobj.close()
    '''
    if type(image_matrix[0][0]) == int:
        save_regular_image(image_matrix, filename)
        
    elif type(image_matrix[0][0]) == str:
        save_compressed_image(image_matrix, filename)
        
    else:
        raise AssertionError("Invalid data type")
    
    
def invert(image_matrix):
    '''
    (int[]) -> int[]
    
    Takes as input a PGM image matrix, and returns the inverted matrix without modifying the input.
    
    >>>invert([[255, 0, 10], [200, 0, 60], [0, 0, 0]])
    [[0, 255, 245], [55, 255, 195], [255, 255, 255]]
    
    >>>invert([[0,1],[1,0]])
    [[255, 254], [254, 255]]
    
    >>>invert([[0,30,0],[255,0,100]])
    [[255, 225, 255], [0, 255, 155]]
    '''
    if not is_valid_image(image_matrix):
        raise AssertionError("Invalid PGM image")
    
    copy = deep_copy(image_matrix)
    
    inverted_image = []
    
    placeholder = []
    
    for i in copy:
        for n in i:
            placeholder.append(255 - n)
            
        inverted_image.append(placeholder)
        
        placeholder = []
        
    return inverted_image


def flip_horizontal(image_matrix):
    '''
    (int[]) -> int[]
    
    Takes as input a PGM image matrix, and returns the flipped matrix without modifying the input.
    
    >>>flip_horizontal([[255, 0, 10], [200, 0, 60], [0, 0, 0]])
    [[10, 0, 255], [60, 0, 200], [0, 0, 0]]
    
    >>>flip_horizontal([[0,1],[1,0]])
    [[1, 0], [0, 1]]
    
    >>>flip_horizontal([[0,30,0],[255,0,100]])
    [[0, 30, 0], [100, 0, 255]]
    '''
    if not is_valid_image(image_matrix):
        raise AssertionError("Invalid PGM image")
    
    copy = deep_copy(image_matrix)
    
    flipped_image = []
    
    for i in copy:
        flipped_image.append(i[::-1])
        
    return flipped_image


def flip_vertical(image_matrix):
    '''
    (int[]) -> int[]
    
    Takes as input a PGM image matrix, and returns the flipped matrix without modifying the input.
    
    >>>flip_vertical([[255, 0, 10], [200, 0, 60], [0, 0, 0]])
    [[0, 0, 0], [200, 0, 60], [255, 0, 10]]
    
    >>>flip_vertical([[0,1],[1,0]])
    [[1, 0], [0, 1]]
    
    >>>flip_vertical([[0,30,0],[255,0,100]])
    [[255, 0, 100], [0, 30, 0]]
    '''
    if not is_valid_image(image_matrix):
        raise AssertionError("Invalid PGM image")
    
    copy = deep_copy(image_matrix)
    
    return copy[::-1]

def crop(image_matrix, startRow, startColumn, distRows, distColumns):
    '''
    (int[]) -> int[]
    
    Takes as input a PGM image matrix, and returns the cropped matrix without modifying the input.
    
    >>>crop([[255, 0, 10], [200, 0, 60], [0, 0, 0]],0,0,2,2)
    [[255, 0], [200, 0]]
    
    >>>crop([[0,1],[1,0]],0,0,1,2)
    [[0, 1]]
    
    >>>crop([[0,30,0],[255,0,100]],1,0,1,2)
    [[255, 0]]
    '''
    if not is_valid_image(image_matrix):
        raise AssertionError("Invalid PGM image")
    
    copy = deep_copy(image_matrix)
    
    copy = copy[startRow: (startRow + distRows)]
    
    cropped_image = []
    
    for i in copy:
        cropped_image.append(i[startColumn:(startColumn + distColumns)])
        
    return cropped_image
    
def find_end_of_repetition(value_list, start, target):
    '''
    (int[]) -> int
    
    Takes as input a row of a PGM image matrix, a start index and a number, and returns the index of the last number in the
    repetition.
    
    >>>find_end_of_repetition([0, 0, 0, 1]],0,0)
    2
    
    >>>find_end_of_repetition([255,255,0,0,255],2,0)
    3
    
    >>>find_end_of_repetition([20,20,20,20,255,20],1,20)
    3
    '''
    copy = deep_copy([value_list])
    
    for i in range(start, len(copy[0])):
        if copy[0][i] != target:
            return (i - 1)
        
    return len(value_list) - 1

def compress(image_matrix):
    '''
    (int[]) -> str[]
    
    Takes as input a PGM image matrix, and returns a compressed PGM image list.
    
    >>>compress([[255, 0, 10], [200, 0, 60], [0, 0, 0]])
    [['255x1', '0x1', '10x1'], ['200x1', '0x1', '60x1'], ['0x3']]
    
    >>>compress([[0,1],[1,0]])
    [['0x1', '1x1'], ['1x1', '0x1']]
    
    >>>compress([[0,30,0],[255,0,100]])
    [['0x1', '30x1', '0x1'], ['255x1', '0x1', '100x1']]
    '''
    if not is_valid_image(image_matrix):
        raise AssertionError("Invalid PGM image")
    
    copy = deep_copy(image_matrix)
    
    compressed_matrix = []
    
    placeholder = []
    
    for i in copy:
        line = i
        
        while line != []:
            current_element = line[0]
            
            length = find_end_of_repetition(line, 0, current_element)
            
            placeholder.append(str(current_element) + "x" + str(length + 1))

            line = line[(length + 1):]
            
        compressed_matrix.append(placeholder)
        
        placeholder = []
        
    return compressed_matrix

def decompress(image_matrix):
    '''
    (str[]) -> int[]
    
    Takes as input a compressed PGM image matrix, and returns a decompressed PGM image list.
    
    >>>decompress([['255x1', '0x1', '10x1'], ['200x1', '0x1', '60x1'], ['0x3']])
    [[255, 0, 10], [200, 0, 60], [0, 0, 0]]
    
    >>>decompress([['0x1', '1x1'], ['1x1', '0x1']])
    [[0,1],[1,0]]
    
    >>>decompress([['0x1', '30x1', '0x1'], ['255x1', '0x1', '100x1']])
    [[0,30,0],[255,0,100]]
    '''
    if not is_valid_compressed_image(image_matrix):
        raise AssertionError("Not a valid compressed PGM image matrix")
    
    decompressed_matrix = []
    
    placeholder = []
    
    for i in image_matrix:
        for n in i:
            sequence = n.split("x")
            sequence[0] = int(sequence[0])
            sequence[1] = int(sequence[1])
            
            for m in range(sequence[1]):
                placeholder.append(sequence[0])
                
        decompressed_matrix.append(placeholder)
        
        placeholder = []
        
    return decompressed_matrix

def process_command(order_string):
    '''
    (str) -> NoneType
    
    Combines all the previous functions.
    
    >>>fobj = open("test1.pgm", "w")
    >>>fobj.write("P2\\n2 2\\n255\\n0 0\\n255 0")
    20
    >>>fobj.close()
    >>>process_command("LOAD<test1.pgm> INV CP SAVE<output1.pgm>")
    >>>load_image("output1.pgm")
    [['255x2'], ['0x1', '255x1']]
    
    >>>fobj = open("test2.pgm", "w")
    >>>fobj.write("P2\\n3 2\\n255\\n0 30 0\\n255 0 100")
    27
    >>>fobj.close()
    >>>process_command("LOAD<test2.pgm> FH FV SAVE<output2.pgm>")
    >>>load_image("output2.pgm")
    [[100, 0, 255], [0, 30, 0]]
    
    >>>fobj = open("test3.pgm", "w")
    >>>fobj.write("P2C\\n3 3\\n255\\n255x1 0x1 10x1\\n200x1 0x1 60x1\\n0x3")
    45
    >>>fobj.close()
    >>>process_command("LOAD<test3.pgm> DC CP<0,0,2,2> SAVE<output3.pgm>")
    >>>load_image("output3.pgm")
    [['255x1', '0x1', '10x1'], ['200x1', '0x1', '60x1'], ['0x3']]
    '''
    image_matrix = []
    
    orders = order_string.split()
    
    for i in orders:
        command = i
        
        if command.count("LOAD") == 1:            
            command = command.strip("LOAD<").strip(">")
            
            image_matrix = load_image(command)
            
        elif command.count("SAVE") == 1:
            command = command.strip("SAVE<").strip(">")
            
            save_image(image_matrix, command)
            
        elif command.count("INV") == 1:
            image_matrix = invert(image_matrix)
            
        elif command.count("FH") == 1:
            image_matrix = flip_horizontal(image_matrix)
            
        elif command.count("FV") == 1:
            image_matrix = flip_vertical(image_matrix)
            
        elif command.count("CR") == 1:
            command = command.strip("CR<").strip(">")
            
            dimensions = command.split(",")
            
            for i in range(len(dimensions)):
                dimensions[i] = int(dimensions[i])
            
            image_matrix = crop(image_matrix, dimensions[0], dimensions[1], dimensions[2], dimensions[3])
            
        elif command.count("CP") == 1:
            image_matrix = compress(image_matrix)
            
        elif command.count("DC") == 1:
            image_matrix = decompress(image_matrix)
            
        else:
            raise AssertionError("Invalid command")
            
            






