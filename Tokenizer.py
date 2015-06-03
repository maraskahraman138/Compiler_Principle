#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Comzyh
# @Date:   2015-06-01 19:05:49
# @Last Modified by:   Comzyh
# @Last Modified time: 2015-06-03 18:38:57
import re
import json
from fa import Epsilon, NFA


def read_lexical():
    line_number = 0
    final = []
    productions = []
    reg = re.compile(r'(?P<left>\w+)\s*=\s*((?P<epsilon>\$)|'
                     '((?P<right>\w+))?\s*\"(?P<terminate>.*)\")')
    for line in open('lex.txt'):
        if line[0] == '#':
            continue
        if line_number == 0:
            final = line[:-1].split(' ')
        else:
            groups = reg.search(line)
            if groups is None:
                continue
            p = groups.groupdict()
            if p['epsilon'] is not None:
                p['epsilon'] = True
            if p['terminate']:
                p['terminate'] = json.loads('"' + p['terminate'] + '"')
            productions.append(p)
        line_number += 1
    print 'lexical loaded, %d lines at all' % line_number
    return final, productions


def create_nfa(final_states_name, productions):
    alphabet = set()
    for i in range(ord(' '), ord('~') + 1):
        alphabet.add(chr(i))
    nfa = NFA(alphabet)
    name_to_state_dict = {}

    def get_state_by_name(name):
        if name not in name_to_state_dict:
            name_to_state_dict[name] = nfa.create_node()
        return name_to_state_dict[name]

    for final_state_name in final_states_name:
        node = get_state_by_name(final_state_name)
        node.data = {'token': final_state_name}
        nfa.final_state.add(node)
        # print 'index: %3d, name: %s' % (node.index, final_state_name)
    for p in productions:
        left_state = get_state_by_name(p['left'])
        if p['epsilon']:
            nfa.add_trans(nfa.S, Epsilon, left_state)
            continue
        if p['right'] is not None:
            f = get_state_by_name(p['right'])
        else:
            f = nfa.S
        for i in p['terminate'][:-1]:
            node = nfa.create_node()
            nfa.add_trans(f, i, node)
            f = node
        nfa.add_trans(f, p['terminate'][-1:], left_state)
    nfa.name_to_state_dict = name_to_state_dict
    return nfa


def tokenizer_over_nfa(string, position, nfa):
    state_set = set()
    state_set.add(nfa.S)
    endpos = position
    for i in range(position, len(string)):
        char = string[i]
        # print 'char: %s' % char
        new_state_set = set()
        for state in state_set:
            # state.show_transfer(char)
            if char in state.transfer:
                new_state_set = new_state_set.union(set(state.transfer[char]))
        if not new_state_set:
            break
        endpos = i
        state_set = new_state_set

    final_states = set()
    for state in state_set:
        if state in nfa.final_state:
            final_states.add(state.data['token'])
    return endpos + 1, final_states, string[position:endpos + 1]


def main():
    print 'Tokenizer by comzyh'
    final, productions = read_lexical()
    nfa = create_nfa(final, productions)
    for key, value in nfa.name_to_state_dict.items():
        print 'index: %d, %s' % (value.index, key)
    # print nfa
    token_table = []
    for line in open('input.txt'):
        token_table_line = []
        pos = 0
        while pos < len(line):
            while pos < len(line) and line[pos] in [' ', '\t', '\n']:
                pos += 1
            if pos < len(line):
                pos, state_set, token = tokenizer_over_nfa(line, pos, nfa)
                token_type = None
                for _type in final:
                    if _type in state_set:
                        token_type = _type
                        break
                token_table_line.append((token_type, token))
        for token_type, token in token_table_line:
            print token,
        print '\n'
        token_table += token_table_line
        # break
    output_file = open('token_table.txt', 'w+')
    for token_type, token in token_table:
        output_file.write('%s\t%s\n' % (token_type, token))
if __name__ == '__main__':
    main()
