#! /usr/bin/env python3
# ------------------------------------------------
# Author:    krishna
# USAGE:
#       top.py <pseudocode file>
# ------------------------------------------------
import fileinput
import sly
import pygraphviz as pgv
import os
import sys


class FlowLexer(sly.Lexer):
    "Tokenize the pseudocode"

    tokens = {IF, ELSE, COND, STATE, PARAN_OPEN, PARAN_CLOSE}

    ignore = ' \t'
    ignore_comment = r'\#.*'

    IF = r'if'
    ELSE = r'else'
    COND = r'\(.+?\)'
    PARAN_OPEN = r'\{'
    PARAN_CLOSE = r'\}'
    STATE = r'.+;'
    
    
    # Line number tracking
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    # def error(self, t):
    #    print('Line %d: Bad character %r' % (self.lineno, t.value[0]))
    #    self.index += 1

class FlowBuilder:
    """Builds Flow chart"""

    # TODO: This is better done as a parser

    attr = {
        'STATE': {
            'shape':'rectangle',
            'style':'rounded,filled',
            'fillcolor':'lightblue'
        },
        'COND': {
            'shape':'diamond',
            # 'style':'rounded',
            'color':'red'
        }
    }
    
    def __init__(self, tokens):
        '''Initialize'''
        self.dot = pgv.AGraph(strict=True, directed=True, rankdir='TD')
        self.tokens = tokens
        self.stack = []
        # self.dot.layout()
        self.generate()

    def generate(self):
        '''Generate the graph'''
        for token in self.tokens:
            self.handleToken(token)

    def getLastToken(self, valuesToIgnore=None):
        "Returns the last token whose value is not in the list of given values to ignore"

        if valuesToIgnore == None:
            valuesToIgnore = ['if', '{'] # , '}']
        else:
            valuesToIgnore.append('if')
            valuesToIgnore.append('{')
            # valuesToIgnore.append('}')
        
        for token in reversed(self.stack):
            if token.value not in valuesToIgnore:
                return token
        
        return None

    def popUntil(self, value):
        "Pops tokens until the given token value is found"

        while self.stack[-1].value != value:
            self.stack.pop()
        
        self.stack.pop()


    def handleToken(self, token):
        '''Handles one token at a time'''

        # Get rid of unwanted characters from State and Condition
        if token.type == 'STATE':
            token.value = token.value[0:-1]
        if token.type == 'COND':
            token.value = token.value[1:-1]
        
        # When a closing } is found, pop all until opening { - and nothing much to do anyway
        if len(self.stack) and (token.value == '}'):
            self.popUntil('{')
            return

        # State
        if token.type in ['STATE', 'COND']:
            # Add a node
            self.dot.add_node(token.value, **self.attr[token.type])

            # Add edge
            if len(self.stack):
                lastToken = self.getLastToken()
                assert lastToken != None, "Probable syntax error"

                if lastToken.type == 'ELSE':
                    lastToken = self.getLastToken(['else'])
                    self.dot.add_edge(lastToken.value, token.value, label='False')
                elif lastToken.type == 'COND':
                    self.dot.add_edge(lastToken.value, token.value, label='True')
                else:
                    self.dot.add_edge(lastToken.value, token.value)

        # Put it on stack at last
        self.stack.append(token)
        

    def write(self, file):
        '''Write to DOT file'''
        self.dot.write(file)


def main():
    '''The Main'''

    lexer = FlowLexer()
    builder = FlowBuilder(lexer.tokenize("".join(fileinput.input())))

    builder.write('flowchart.dot')
    os.system('dot -T jpg -o flowchart.jpg flowchart.dot')

if __name__ == '__main__':
    main()
