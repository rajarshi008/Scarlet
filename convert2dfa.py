from ltlf2dfa.parser.ltlf import LTLfParser
from graphviz import Source
from formulaTree import Formula
import random

class DFA:
	def __init__(self, init_state, final_states, transitions):
		self.final_states = final_states
		self.init_state = init_state
		self.transitions = transitions
		self.states = transitions.keys()
		self.alphabet = list(transitions[init_state].keys())
		self.current_state = self.init_state

		# Calculating number of words of length 0 accepted of length 0 from a state
		self.number_of_words = {(state, 0):int(state in self.final_states) for state in self.states}
		self.calculated_till = 0

	def is_word_in(self, word):
		'''
		checks if a word belongs to the language of the DFA
		'''
		state = self.init_state
		for letter in word:
			state = self.transitions[state][letter]
		return state in self.final_states

	def complement(self):
		'''
		returns a complement of the self object
		'''
		comp_final_states = [state for state in self.states if state not in self.final_states]
		d = DFA(self.init_state, comp_final_states, dict(self.transitions))
		return d

	def show(self):
		'''
		Produces an image of the DFA
		'''
		dot_str =  "digraph g {\n"

		dot_str += ('__start0 [label="start" shape="none"]\n')

		for s in self.states:
			if s in self.final_states:
				shape = "doublecircle"
			else:
				shape = "circle"
			dot_str += ('{} [shape="{}" label="{}"]\n'.format(s, shape, s))

		dot_str += ('__start0 -> {}\n'.format(self.init_state))

		for s1 in self.transitions.keys():
			tran = self.transitions[s1]
			for letter in tran.keys():
				dot_str += ('{} -> {}[label="{}"]\n'.format(s1, tran[letter], letter))
		dot_str += ("}\n")

		s = Source(dot_str, filename="test.gv", format="png")
		s.view()
		

	def save(self, filename):
		with open(filename + ".dot", "w") as file:
			file.write("digraph g {\n")
			file.write('__start0 [label="" shape="none]\n')

			for s in self.states:
				if s in self.final_states:
					shape = "doublecircle"
				else:
					shape = "circle"
				file.write('{} [shape="{}" label="{}"]\n'.format(s, shape, s))

			file.write('__start0 -> {}\n'.format(self.init_state))

			for s1 in self.transitions.keys():
				tran = self.transitions[s1]
				for letter in tran.keys():
					file.write('{} -> {}[label="{}"]\n'.format(s1, tran[letter], letter))
			file.write("}\n")


	def __str__(self):
		'''
		prints the dfas in a readable format
		'''
		output_str = ''
		output_str += 'Init: '+str(self.init_state) + '\n'
		output_str += 'States: '+','.join(list(map(str, self.states))) + '\n'
		output_str += 'Transitions:\n'
		for state in self.transitions:
			for letter in self.alphabet:
				output_str += str(state)+ '-'+str(letter)+'->'+str(self.transitions[state][letter])+','
			output_str += '\n'
		output_str += 'Final states: '+','.join(list(map(str,self.final_states)))
		return output_str

	def generate_all_accepting_words(self):
		'''
		returns all words that are accepted by DFA
		'''
		return self.generate_accepting_words(self.init_state)


	def generate_accepting_words(self, state):
		'''
		returns all words that are accepted by a DFA from a given state 
		'''
		all_words = []
		if state in self.final_states:
			all_words += ['']

		for letter in self.alphabet:
			successor_states = self.transitions[state][letter]

			for next_state in successor_states:
				all_words += [letter+word for word in self.generate_accepting_words(next_state)]

		return all_words

	def generate_num_accepting_words(self, length):
		'''
		returns the number of words that are accepted of a particular length
		'''
		if self.calculated_till > length:
			return
		else:
			for i in range(self.calculated_till+1,length+1):
				self.number_of_words.update({(state, i):0 for state in self.states})
				for state in self.states:
					for letter in self.alphabet:
						for next_state in self.transitions[state][letter]:
							self.number_of_words[(state, i)] += self.number_of_words[(next_state, i-1)]



	def generate_random_word(self):
		'''
		returns any random word that is accepted
		'''
		random_length = random.randint(0,100)
		return self.generate_random_word_length(random_length)

	# Algorithm taken from https://link.springer.com/article/10.1007/s00453-010-9446-5
	def generate_random_word_length(self, length):
		'''
		returns a random word of a particular length that is accepted
		'''
		if self.calculated_till < length:
			self.generate_num_accepting_words(length)

		rand_word = tuple()
		state = self.init_state
		for i in range(1,length+1):
			transition_list = []
			prob_list = []
			for letter in self.alphabet:
				for next_state in self.transitions[state][letter]:
					transition_list.append((letter, next_state))
					prob_list.append(self.number_of_words[(next_state, length-i)]/self.number_of_words[(state, length-i+1)])

			next_transition = random.choices(transition_list, weights=prob_list)[0]
			state = next_transition[1]
			
			rand_word+=(next_transition[0],)
		return rand_word




def atom2letters(atom_string, letter2pos):
	# preprocessing of atom strings
	

	alphabet = list(letter2pos.keys())


	sign = {letter:0 for letter in alphabet}
	if atom_string != 'true':
		atom_string = atom_string.replace(' ' ,'')
		atoms = atom_string.split('&')
		for prop in atoms:
			if prop[0]=='~':
				sign[prop[1]] = -1
			else:
				sign[prop[0]] = 1
	letter_list = [[]]
	for letter in alphabet:
		new_letter_list = []
		if sign[letter] == 0:
			for l in letter_list:
				new_letter_list.append(l+[0])
				new_letter_list.append(l+[1])
		
		if sign[letter] == 1:
			for l in letter_list:
				new_letter_list.append(l+[1])

		if sign[letter] == -1:
			for l in letter_list:
				new_letter_list.append(l+[0])
		letter_list = new_letter_list

	letter_list = [tuple(l) for l in letter_list]
	return letter_list



		

def ltl2dfa(formula, letter2pos):
	# convert formula into formulastring
	# possiblilties to use the infix or the prefix form

	#formula_str = formula.prettyPrint()
	formula_str = formula.prettyPrint()

	parser = LTLfParser()
	
	formula = parser(formula_str)       # returns an LTLfFormula

	#d = atom2letters(alphabet = alphabet)
	original_dfa = formula.to_dfa() # using atoms
	


	d = original_dfa
	return dot2DFA(original_dfa, letter2pos)
	# prints "G(a -> X (b))"

	# create a map from propostitions to the corresponding digits



def dot2DFA(dot_string, letter2pos):

	dfa_info = dot_string.split('\n')
	mode = ''
	transitions = {}
	for line in dfa_info:
		
		if line == '}':
			break

		if 'doublecircle' in line:
			line = line.split(']')[1]
			line = line.replace(' ', '')
			final_states = line.split(';')[1:-1]

		if '->' in line and mode != 'transitions':
			line = line.replace(' ', '')
			init_state = line.split('->')[1][:-1]
			mode = 'transitions'
			continue
		
		if mode == 'transitions':
			edge, label_info = line.split('[')

			edge = edge.replace(' ', '')
			first_state, second_state = edge.split('->')
			
			label = label_info.split('\"')[1]
			letters = atom2letters(label, letter2pos)
			for letter in letters:
				try:
					transitions[first_state][letter] = second_state
				except:
					transitions[first_state] = {letter:second_state}


	formula_dfa = DFA(init_state, final_states, transitions)
	formula_dfa.show()
	#print(formula_dfa)
	return formula_dfa

# letter2pos = {'p':0, 'q':1, 'r':2}
# dfa = (ltl2dfa('dummy', letter2pos))
# dfa_c = dfa.complement()
# print(dfa_c)
# dfa_c.show()
# print(dfa_c.generate_random_word_length(10))
#print(str(dfa))