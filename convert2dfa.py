
from graphviz import Source
import random
from ltlf2dfa.parser.ltlf import LTLfParser
from Scarlet.formulaTree import Formula

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

	def show(self, filename="test.gv"):
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
		
		s = Source(dot_str, filename=filename, format="png")
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
						next_state = self.transitions[state][letter]
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


	def generate_random_words_in_batch(self, length_range, batch_size):

		epsilon = 0.01
		
		#if self.calculated_till < length_range[1]:
		#	self.generate_num_accepting_words(length_range[1])

		word_list = []
		last_path = [] 
		prob_dict = {}
		length_list = list(range(length_range[0], length_range[1]+1))
		valid_length = []
		for l in length_list:
			if self.number_of_words[(self.init_state,l)] != 0:
				valid_length.append(l)

		if valid_length == []:
			raise Exception('No traces with the given lengths') 

		transition_count = {}

		num=0
		for num in range(batch_size):
			
			rand_word = tuple()
			state = self.init_state
			length = random.choice(valid_length)
			
			
			for i in range(1,length+1):
				non_sink_transitions = [] #letters which lead to some accepting states
				prob_list = []
				count_list = []

				for letter in self.alphabet:
					
					next_state = self.transitions[state][letter]
					
					if (state, letter, next_state) not in transition_count:
						transition_count[(state, letter, next_state)] = 0
					
					#print(next_state, self.number_of_words[(next_state, length-i)], length-i)
					if self.number_of_words[(next_state, length-i)] != 0:
						non_sink_transitions.append((state, letter, next_state))
						


					count_list.append(transition_count[(state, letter, next_state)])


				num_accepted_trans = len(non_sink_transitions)
				total_count = sum(count_list)
				
				for j in range(len(self.alphabet)):
					next_state = self.transitions[state][self.alphabet[j]]
					if self.number_of_words[(next_state, length-i)] != 0:
						if num_accepted_trans == 1:
							transition_prob = 1
						elif total_count == 0:
							transition_prob = (1/num_accepted_trans)
						else:
							transition_prob = (1/num_accepted_trans)*(1-(count_list[j]/total_count))
					
						prob_list.append(transition_prob)
				
				
				
				prob_list = [(i/sum(prob_list)) for i in prob_list]
	
				next_transition = random.choices(non_sink_transitions, weights=prob_list)[0]
				transition_count[next_transition] += 1
				#print("Count", transition_count)
				state = next_transition[2]
				rand_word+=(next_transition[1],)
			
			word_list.append(rand_word)	

		return word_list



def atom2letters(atom_string, letter2pos, is_word):
	# preprocessing of atom strings
	atom_string = atom_string.replace(' ' ,'')

	alphabet = list(letter2pos.keys())

	atomlist = atom_string.split('|')
	all_letter_list= set()
	for atom_disjuncts in atomlist:
		sign = {letter:0 for letter in alphabet}
		if atom_string != 'true':
			atoms = atom_disjuncts.split('&')
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

		letter_list = set(tuple(l) for l in letter_list)
		all_letter_list= all_letter_list.union(letter_list)
	
	return list(all_letter_list)


def atom2letters_new(atom_string, letter2pos, is_word):

	
	alphabet = list(letter2pos.keys())
	
	all_letters = set([tuple()])
	for atom in alphabet:
		new_all_letters = {letter+(0,) for letter in all_letters}			
		new_all_letters = new_all_letters.union({letter+(1,) for letter in all_letters})
		all_letters = new_all_letters

	if is_word:
		all_letters = {i for i in all_letters if sum(i)==1}

	if atom_string == 'true':
		
		return all_letters

	if atom_string == 'false':

		no_letters = []
		return no_letters

	parser = LTLfParser()
	atom_formula = parser(atom_string)
	t = (atomformula2letters(atom_formula, letter2pos, all_letters, is_word))
	return t


def atomformula2letters(atom_formula, letter2pos, all_letters, is_word):

	try:
		op = atom_formula.operator_symbol
		if op == '&':
			letter_set = all_letters
			for child_atom in atom_formula.formulas:
				l = atomformula2letters(child_atom, letter2pos, all_letters, is_word)
				letter_set = letter_set.intersection(l)
			

		elif op == '|':
			letter_set = set()
			for child_atom in atom_formula.formulas:
				l = atomformula2letters(child_atom, letter2pos, all_letters, is_word)
				letter_set = letter_set.union(l)

		
		elif op == '!':
			child_atom = atom_formula.f
			l = atomformula2letters(child_atom, letter2pos, all_letters, is_word)
			letter_set = all_letters.difference(l)
			

	except:
		alphabet = list(letter2pos.keys())
		atom_list = atom_formula.find_labels()
		assert(len(atom_list)==1)
		letter_set = set([tuple()])
		for atom in alphabet:
			new_letter_set = set()
			if atom in atom_list:
				new_letter_set = new_letter_set.union({letter+(1,) for letter in letter_set})
			else:
				new_letter_set = new_letter_set.union({letter+(0,) for letter in letter_set})			
				new_letter_set = new_letter_set.union({letter+(1,) for letter in letter_set})
			letter_set = new_letter_set
		if is_word:
			letter_set = {i for i in letter_set if sum(i)==1}
	return letter_set



def ltl2dfa(formula, letter2pos, is_word):
	# convert formula into formulastring
	# possiblilties to use the infix or the prefix form

	formula_str = formula.prettyPrint()

	parser = LTLfParser()
	
	formula = parser(formula_str) # returns an LTLfFormula

	#d = atom2letters(alphabet = alphabet)
	original_dfa = formula.to_dfa() #using atoms
	return dot2DFA(original_dfa, letter2pos, is_word)
	
	# create a map from propostitions to the corresponding digits



def dot2DFA(dot_string, letter2pos, is_word):

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
			letters = atom2letters_new(label, letter2pos, is_word)
			if first_state == '3':
				#print(label, letters)
				pass
			for letter in letters:
				try:
					transitions[first_state][letter] = second_state
				except:
					transitions[first_state] = {letter:second_state}


	formula_dfa = DFA(init_state, final_states, transitions)

	return formula_dfa

#letter2pos = {'p':0, 'q':1, 'r':2, 's':3}
#print(atom2letters_new('~p & ~r', letter2pos))

# dfa = (ltl2dfa('dummy', letter2pos))
# dfa_c = dfa.complement()
# print(dfa_c)
# dfa_c.show()
# print(dfa_c.generate_random_word_length(10))
#print(str(dfa))

# ltl = "|(X(X(q)),&(F(p),X(q)))"
# f = Formula().convertTextToFormula(ltl)
# letter2pos = {'p':0, 'q':1}
# dfa = ltl2dfa(f, letter2pos)
# dfa1 = dfa.complement()

# # print("Started")
# l= dfa1.generate_random_words_in_batch((10,15), 100000)
# # print("Ended")
# for word in l:
#  	if dfa.is_word_in(word):
#  		print(word)

#dfa = DFA(1, [2], {1:{'a':2, 'b':2, 'c':1}, 2:{'a':1, 'b':3, 'c':3}, 3:{'a':3, 'b':3, 'c':3}})
#dfa.show()
