#!/usr/bin/python
#
# Brainfuck Interpreter
# Copyright 2011 Sebastian Kaspari
#

import sys
import time
import getopt


def execute(input_file,use_string=0):
    if (use_string==1):
        ans = evaluate(input_file)
        return ans
    else:
        f = open(input_file, "r")
        ans = evaluate(f.read())
        f.close()
        return ans


def evaluate(code, input_buffer=None, timeout=5):
    """
    Modified brainfuck interpreter based on https://github.com/pocmo/Python-Brainfuck/blob/master/brainfuck.py

    Executes string of brainfuck code and returns a string of output

    Has a timeout function to limit execution time.

    If the function times out, it will not return the output buffer, even if
    it had something in it.

    if input_buffer is not None, it will treat it as stdin

    """
    output = ""
    code = cleanup(list(code))
    bracemap = buildbracemap(code)
    cells, codeptr, cellptr = [0], 0, 0

    if input_buffer != None:
        input_buffer = list(input_buffer)

    start = time.time()
    while (time.time() - start < timeout):
        if(codeptr < len(code)):
            command = code[codeptr]
            if command == ">":
                cellptr += 1
                if cellptr == len(cells):
                    cells.append(0)
            if command == "<":
                cellptr = 0 if cellptr <= 0 else cellptr - 1
            if command == "+":
                cells[cellptr] = cells[cellptr] + 1 if cells[cellptr] < 255 else 0
            if command == "-":
                cells[cellptr] = cells[cellptr] - 1 if cells[cellptr] > 0 else 255
            if command == "[" and cells[cellptr] == 0:
                codeptr = bracemap[codeptr]
            if command == "]" and cells[cellptr] != 0:
                codeptr = bracemap[codeptr]
            if command == ".":
                output += chr(cells[cellptr])
            if command == ",":
                if input_buffer:
                    cells[cellptr] = ord(input_buffer.pop(0))
            codeptr += 1
        else:
            return output
    return ""


def cleanup(code):
    return list([x for x in code if x in ['.', ',', '[', ']', '<', '>', '+', '-']])


def buildbracemap(code):
    temp_bracestack, bracemap = [], {}

    for position, command in enumerate(code):
        if command == "[":
            temp_bracestack.append(position)
        if command == "]":
            start = temp_bracestack.pop()
            bracemap[start] = position
            bracemap[position] = start
    return bracemap


def main(argv):
    # file I/O
    inputfile = ''
    outputfile = ''
    input_code = ''
    try:
        opts, args = getopt.getopt(argv,"hs:i:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
            print(('Input file is %s' % inputfile)
        elif opt in ("-o", "--ofile"):
            outputfile = arg
            print('Output file is %s' % outputfile)
        elif opt == '-s':
            input_code = arg



    # print result
    if(input_code!=''):
        genetic_code = execute(input_code,1)
    else:
        genetic_code = execute(inputfile)
    print(genetic_code)



if __name__ == "__main__":
    main(sys.argv[1:])
