'''
Generating LTL patterns from sample, named directed ltl
'''

import heapq as hq
import time
import logging
from Scarlet.booleanSubsetCover import BooleanSetCover
from Scarlet.sample import Sample, Trace, lineToTrace
from Scarlet.formulaTree import Formula


epsilon=tuple()
inf_pos = 'end'
len_atom_table = {}


'''
Fixing some notations with examples:

- We read words from samples as 1,0,0;1,0,1;0,1,1. 
- We say each part of the word as letter, e.g. 1,0,0 
- 0->p, 1->q, 2->r,... are the propositions
- Examples of atoms are (0,), (1,2). (1,2) is an atom of width 2 which means (q & r).
- 'inv' denotes if the sample has been inversed or not, i.e. positives as negatives and vice-versa.
'''


def neg_props(atom: tuple)-> list:
	'''
		creates the dual atom
	'''
	neg_props = [] 
	for i in atom:
		if i[0]=='+':
			neg_props.append(('-'+i[1:],))
		else:
			neg_props.append(('+'+i[1:],))
	return neg_props


def len_atom(atom: tuple, inv: bool)->int:
	'''
		Calculates length of an atom
	'''
	try:
		return len_atom_table[(atom, inv)]
	except:
		if inv:
			len_atom_table[(atom, inv)] = 2*len(atom)+len([1 for i in atom if i[0]=='+'])-1
			return len_atom_table[(atom, inv)]
		else:
			len_atom_table[(atom, inv)] = 2*len(atom)+len([1 for i in atom if i[0]=='-'])-1
			return len_atom_table[(atom, inv)]



def is_sat(letter:tuple, atom:tuple, is_end: bool) -> bool:
	'''
		checking satisfiability of an atom in a letter, e.g. (0,) and (2,) is true in (1,0,1) but (1,) is not
	'''
	for pos in atom:
		if pos == '+-1' and not is_end:
			return False
		elif pos == '--1' and is_end:
			return False
		elif pos != '+-1' and pos != '--1':
			if letter[int(pos[1:])] == (pos[0]!='+'):
				return False
	return True

def dltl2Formula(dltl_tuple: tuple, inv: bool, alphabet: list):
	'''
		it converts dirtected dltl data-structures to an LTL formula
	'''
	if dltl_tuple == tuple():
		return None

	if inv:
		first_atom = dltl_tuple[1]
		if first_atom[0][0] == '-':
			form_atom = Formula(alphabet[int(first_atom[0][1:])])
		else:
			form_atom = Formula(['!', Formula(alphabet[int(first_atom[0][1:])])])

		for i in first_atom[1:]:
			if i[0] == '-':
				form_atom = Formula(['|', form_atom, Formula(alphabet[int(i[1:])])])
			else:
				form_atom = Formula(['|', form_atom, Formula(['!', Formula(alphabet[int(i[1:])])])])
		
		if len(dltl_tuple)>2:
			next_formula = Formula(['|', form_atom, dltl2Formula(dltl_tuple[2:], inv, alphabet)])
		else:
			next_formula = form_atom
		
		first_digit = int(dltl_tuple[0].strip('>'))
		if dltl_tuple[0][0]=='>':
			next_formula = Formula(['G', next_formula])

		for i in range(first_digit):
			next_formula = Formula(['X', next_formula])

	else:
		first_digit = int(dltl_tuple[0].strip('>'))
		first_atom = dltl_tuple[1]
		if first_atom[0][0] == '+': 
			form_atom = Formula(alphabet[int(first_atom[0][1:])])
		else:
			form_atom = Formula(['!', Formula(alphabet[int(first_atom[0][1:])])])

		for i in first_atom[1:]:
			if i[0] == '+':
				form_atom = Formula(['&', form_atom, Formula(alphabet[int(i[1:])])])
			else:
				form_atom = Formula(['&', form_atom, Formula(['!', Formula(alphabet[int(i[1:])])])])
		
		if len(dltl_tuple)>2:
			next_formula = Formula(['&', form_atom, dltl2Formula(dltl_tuple[2:], inv, alphabet)])
		else:
			next_formula = form_atom
		for i in range(first_digit):
			next_formula = Formula(['X', next_formula])
		if dltl_tuple[0][0]=='>':
			next_formula = Formula(['F', next_formula])

	return next_formula

class Dltl:
	'''
	Data structure for Directed Formulas (dltl)
	'''
	def __init__(self, vector, inv):
		self.vector = vector
		self.inv = inv

	def __eq__(self, other):
		if other is None:
			return False
		else:
			return (self.vector == other.vector) and (self.inv == other.inv)

	def __ne__(self, other):
		return not self == other

	def __hash__(self):

		return hash((self.vector,self.inv))


	def extenddltl(self, diff: int, atoms: tuple, upper_bound: int, operators=['F','G','X','&','|','!']):
		'''
		Extends dltl with diff and atom to increase its length 
		'''
		dltl_list = []
		
		#Given difference d, the process of appending >0,>1, ..., >d-1 atoms to the dltl
		if 'X' not in operators:
			diff = 0

		if (not self.inv and 'F' in operators) or (self.inv and 'G' in operators):
			for atom in atoms:
				#For eliminating p>0p type dltls
				for i in range(diff):
					if self.vector != epsilon and atom == self.vector[-1] and i==0:
						continue

					#new_dltl = dltl+('>'+str(i),atom)
					new_dltl = Dltl(self.vector+('>'+str(i),atom), self.inv)	
					base_len = self.size + 1 + (i+1) + len_atom(atom, self.inv)
					
					if base_len >= upper_bound:
						break
					new_dltl.size = base_len
					
					dltl_list.append(new_dltl)

		#Given difference d, the process of appending >d,=d atoms to the dltl
		for atom in atoms:#('+1', '-0')
			if 'X' in operators:
				if self.vector != epsilon or not self.inv:

					new_dltl = Dltl(self.vector+(str(diff),atom), self.inv)
					base_len = self.size + 1 + diff + len_atom(atom, self.inv)
					if base_len < upper_bound:
						new_dltl.size = base_len
						dltl_list.append(new_dltl)
			else:
				if self.vector == epsilon or not self.inv:
					new_dltl = Dltl(self.vector+('0', atom),self.inv)
					new_dltl = len_atom(atom, self.inv)
					dltl_list.append(new_dltl)
					

			if (not self.inv and 'F' in operators) or (self.inv and 'G' in operators):
				new_dltl = Dltl(self.vector+('>'+str(diff),atom),self.inv)
				base_len = self.size + 1 + (diff+1) + len_atom(atom, self.inv)
				
				if base_len < upper_bound:
					new_dltl.size = base_len
					dltl_list.append(new_dltl)


		return dltl_list



class findDltl:
	'''
	Search algorithm for dltl
	'''
	def __init__(self, sample, operators, last, thres, upper_bound):
		
		self.sample = sample 
		self.operators = operators
		self.last=last
		self.thres = thres
		self.upper_bound = upper_bound

		self.num_positives = len(self.sample.positive)
		self.num_negatives = len(self.sample.negative)

		self.positive_set = {i for i in range(len(self.sample.positive))}
		self.negative_set = {i for i in range(len(self.sample.negative))}
		self.full_cover = len(self.positive_set) + len(self.negative_set)

		#Value determining if "!" is allowed in the operators
		self.neg = '!' in self.operators
		
		#Calculates the maximum length of the traces
		try:
			self.max_positive_length = max(len(trace) for trace in self.sample.positive)
		except:
			self.max_positive_length = 0

		try:
			self.max_negative_length = max(len(trace) for trace in self.sample.negative)
		except:
			self.max_negative_length = 0
		'''
		Initializing DP tables: 
	 	
	 	-Ind_table: For a (word, position, atom) stores all the positions the atom is satisfied in the word starting from the position (including the position)
		-R_table: For (length, width) stores dictionaries for all the dltls of that length and width along with their end positions in all the words in the sample
		-R_table_inv: R_table for the inv traces
		-letter2atom_table: For (letter, width) stores all the possible atoms of that width that is satisfiable in that letter
		-len_atom_table: Stores length of an atom
		-len_dltl: Stores dltl for different lengths
		'''
		self.ind_table = {}
		self.R_table = {}
		self.cover_set = {} 

		self.len_dltl = {}
		self.letter2atom_table= {}


		#Precomputing the Ind_table for atoms of width 1
		
		self.preComputeInd_init()
 
	#Calculates length of an atom both with inv true and false


	
	def letter2atoms(self, letter:tuple, width:int, inv: bool):
		'''
		Calculates all possible atoms of given width from a given letter
		'''	
		try:
			#checks if it is already calculated and stored
			if self.neg:
				return self.letter2atom_table[(letter, width, '+-')]
			else:
				if inv:
					return self.letter2atom_table[(letter, width, '-')]
				else:
					return self.letter2atom_table[(letter, width, '+')]
		except:
			#calculates width 1 satisfiable atoms
			if width==0:
				return tuple()

			if width==1:
				if self.neg:
					self.letter2atom_table[(letter, width, '+-')] = [('+'+str(i),) for i in range(len(letter)) if letter[i]==1] + \
																	[('-'+str(i),) for i in range(len(letter)) if letter[i]==0]
					return self.letter2atom_table[(letter, width, '+-')]
				else:
					if inv:
						self.letter2atom_table[(letter, width, '-')] = [('-'+str(i),) for i in range(len(letter)) if letter[i]==0]
						return self.letter2atom_table[(letter, width, '-')]
					else:
						self.letter2atom_table[(letter, width, '+')] = [('+'+str(i),) for i in range(len(letter)) if letter[i]==1]
						return self.letter2atom_table[(letter, width, '+')]
			else:
				#recursively calculates for width >1
				atoms = [] 
				if self.neg:
					for i in range(len(letter)):
						if letter[i]==1:
							atoms+=list(map(lambda x: ('+'+str(i),)+x, self.letter2atoms(tuple([2]*(i+1))+letter[i+1:], width-1, inv)))
						if letter[i]==0:
							atoms+=list(map(lambda x: ('-'+str(i),)+x, self.letter2atoms(tuple([2]*(i+1))+letter[i+1:], width-1, inv)))
					self.letter2atom_table[(letter,width, '+-')] = atoms
					return self.letter2atom_table[(letter,width,'+-')]

				else:
					if inv:
						for i in range(len(letter)):
							if letter[i]==0:
								atoms+=list(map(lambda x: ('-'+str(i),)+x, self.letter2atoms(tuple([2]*(i+1))+letter[i+1:], width-1, inv)))
						self.letter2atom_table[(letter, width, '-')] = atoms
						return self.letter2atom_table[(letter, width, '-')]
					else:
						for i in range(len(letter)):
							if letter[i]==1:
								atoms+=list(map(lambda x: ('+'+str(i),)+x, self.letter2atoms(tuple([2]*(i+1))+letter[i+1:], width-1, inv))) 
						self.letter2atom_table[(letter, width,'+')] = atoms
						return self.letter2atom_table[(letter, width, '+')]

							
				#stores the calculated ones in the dp_table
				return self.letter2atom_table[(letter,width)]

	def genPossibleAtoms(self, letter, width, inv, is_end):
		'''
		Adding atoms for last position
		'''
		atoms = []
		for i in range(1,width+1):
			atoms+=self.letter2atoms(letter, i, inv)
		if self.last:
			if is_end:
				atoms+= [('+-1',)]
				for i in range(1, width):
					atoms+=list(map(lambda x: x+('+-1',), self.letter2atoms(letter, i, inv)))
			else:
				atoms+= [('--1',)]
				for i in range(1, width):
					atoms+=list(map(lambda x: x+('--1',), self.letter2atoms(letter, i, inv)))
		return atoms


	def preComputeInd_init(self):
		'''
		Computing the ind_table for atoms of width 1
		'''
		self.all_atoms = {1: set()}
		#print(width)	
		if self.neg:
			for trace in self.sample.positive+self.sample.negative:
				for letter in trace.vector:	
				
					self.all_atoms[1]= self.all_atoms[1].union(set(self.letter2atoms(letter, 1, True)))
					if self.last:
						self.all_atoms[1]= self.all_atoms[1].union(set(map(lambda x: x+('+-1',), self.letter2atoms(letter, 0, True))))
						self.all_atoms[1]= self.all_atoms[1].union(set(map(lambda x: x+('--1',), self.letter2atoms(letter, 0, True))))
		else:
			for trace in self.sample.positive:
				for letter in trace.vector:	
					self.all_atoms[1] = self.all_atoms[1].union(set(self.letter2atoms(letter, 1, False)))
					if self.last:
						self.all_atoms[1]= self.all_atoms[1].union(set(map(lambda x: x+('+-1',), self.letter2atoms(letter, 0, False))))	
						#self.all_atoms[i]= self.all_atoms[i].union(set(map(lambda x: x+('--1',), self.letter2atoms(letter, i-1, True))))

			for trace in self.sample.negative:
				for letter in trace.vector:	
					self.all_atoms[1]= self.all_atoms[1].union(set(self.letter2atoms(letter, 1, True)))
					if self.last:
						#self.all_atoms[i]= self.all_atoms[i].union(set(map(lambda x: x+('+-1',), self.letter2atoms(letter, i-1, False))))
						self.all_atoms[1]= self.all_atoms[1].union(set(map(lambda x: x+('--1',), self.letter2atoms(letter, 0, True))))

		for word_vec in self.sample.positive + self.sample.negative:
				
				word=word_vec.vector_str

				#We represent last symbol by -1
				self.ind_table[(word, len(word_vec), ('+-1',))] = []
				self.ind_table[(word, inf_pos, ('+-1',))] = []
				for pos in range(len(word_vec)-1, -1, -1):
					self.ind_table[(word, pos, ('+-1',))] = [len(word_vec)-1]

				self.ind_table[(word, len(word_vec), ('--1',))] = []
				self.ind_table[(word, inf_pos, ('--1',))] = []
				for pos in range(len(word_vec)-1, -1, -1):
					self.ind_table[(word, pos, ('--1',))] = list(range(pos,len(word_vec)-1))

				for atom in self.all_atoms[1]:
					self.ind_table[(word, inf_pos, atom)]=[]
					self.ind_table[(word, len(word_vec), atom)]=[]
					for pos in range(len(word_vec)-1,-1,-1):
						
						if atom[0][1:] != '-1':
							if word_vec.vector[pos][int(atom[0][1:])] == (atom[0][0]=='+'):#checking if atom starts with ! implicitly
								self.ind_table[(word, pos, atom)]=[pos]+self.ind_table[(word, pos+1, atom)]
							else:
								self.ind_table[(word, pos, atom)]=self.ind_table[(word, pos+1, atom)]

				
	
	def preComputeInd_next(self, width: int):
		'''
		Computing the ind_table for atoms of higher width
		'''
		try:
			self.all_atoms[width]
			return
		except:
			self.all_atoms[width] = set()
			if self.neg:
				for trace in self.sample.positive+self.sample.negative:
					for letter in trace.vector:	
					
						self.all_atoms[width]= self.all_atoms[width].union(set(self.letter2atoms(letter, width, True)))
						if self.last:
							self.all_atoms[width]= self.all_atoms[width].union(set(map(lambda x: x+('+-1',), self.letter2atoms(letter, width-1, True))))
							self.all_atoms[width]= self.all_atoms[width].union(set(map(lambda x: x+('--1',), self.letter2atoms(letter, width-1, True))))
			else:
				for trace in self.sample.positive:
					for letter in trace.vector:	
						self.all_atoms[width] = self.all_atoms[width].union(set(self.letter2atoms(letter, width, False)))
						if self.last:
							self.all_atoms[width]= self.all_atoms[width].union(set(map(lambda x: x+('+-1',), self.letter2atoms(letter, width-1, False))))
							#self.all_atoms[i]= self.all_atoms[i].union(set(map(lambda x: x+('--1',), self.letter2atoms(letter, i-1, True))))

				for trace in self.sample.negative:
					for letter in trace.vector:	
						
						self.all_atoms[width]= self.all_atoms[width].union(set(self.letter2atoms(letter, width, True)))
						if self.last:
							#self.all_atoms[i]= self.all_atoms[i].union(set(map(lambda x: x+('+-1',), self.letter2atoms(letter, i-1, False))))
							self.all_atoms[width]= self.all_atoms[width].union(set(map(lambda x: x+('--1',), self.letter2atoms(letter, width-1, True))))

			for word_vec in self.sample.positive + self.sample.negative:
				
				word=word_vec.vector_str	
			
				for atom in self.all_atoms[width]:
					self.ind_table[(word, inf_pos, atom)]=[]
					self.ind_table[(word, len(word_vec), atom)]=[]
					for pos in range(len(word_vec)):
						set1=set(self.ind_table[(word,pos,(atom[0],))])
						for j in atom[1:]:
							set1=set1.intersection(set(self.ind_table[(word,pos,(j,))]))

						self.ind_table[(word, pos, atom)]=sorted(list(set1))



	def add2dltl(self, dltl1: Dltl, dltl2: Dltl):
		'''
		Generates a dltl of width w+1 from dltls of width 1 and width w
		'''
		if dltl1.vector == tuple() or dltl2.vector == tuple():
			return None


		dltl_no1 = dltl1.vector[0::2]
		dltl_no2 = dltl2.vector[0::2]
		base_len = dltl1.size
		
		if dltl_no1 != dltl_no2:
			return None
		else:
			n_dltl = Dltl(epsilon, dltl1.inv)
			for i in range(len(dltl2.vector)):
				if isinstance(dltl2.vector[i],str):
					n_dltl.vector+=(dltl2.vector[i],)
				else:
					if dltl2.vector[i][0] in dltl1.vector[i]:
						n_dltl.vector+=(dltl1.vector[i],)
						continue

					for prop in dltl1.vector[i]:
						if prop[1:] == dltl2.vector[i][0][1:]:
							return None
					
					n_dltl.vector+=(tuple(sorted(dltl1.vector[i]+dltl2.vector[i])),)
					base_len += 1+len_atom(dltl2.vector[i], dltl1.inv) 

			final_dltl = n_dltl

			if final_dltl.vector == dltl1.vector or base_len >= self.upper_bound:
				return None

			final_dltl.size = base_len

			return final_dltl

	def genSequence(self, dltl_lengths):
		'''
		Generates the enumeration order	of generating new dltl by increasing lengths
		'''
		seq=[]
		curr_sum = dltl_lengths[0]+1
		m = max(self.max_positive_length,self.max_negative_length)

		while curr_sum + 2 < self.upper_bound:
			
			for j in dltl_lengths:
				if j >= curr_sum:
					break
				i = curr_sum - j	
				if i >= m:
					continue
				seq.append((j,i))
				
			curr_sum=curr_sum+1
		return seq 



	def incrLength(self, sl_length, width):
		''' 
		Length increasing algortihm for finding dltls
		''' 

		dltl_dict = self.R_table[(sl_length-1,width)]
		new_dltl_dict={}

		self.len_dltl[(sl_length, width)] = {}
		dltl_lengths = sorted(list(self.len_dltl[(sl_length-1,width)]))
		seq = self.genSequence(dltl_lengths)

		for (length,i) in seq:
			
			if length+i+2 >= self.upper_bound:
				break

			for dltl in self.len_dltl[(sl_length-1,width)][length]:
				
				pve_endpos_list = dltl_dict[dltl][0]
				nve_endpos_list = dltl_dict[dltl][1]
				
				if dltl.inv:
					base_traces = self.sample.negative
					base_traces_num = self.num_negatives
					base_endpos_list = nve_endpos_list
				else:
					base_traces = self.sample.positive
					base_traces_num = self.num_positives
					base_endpos_list = pve_endpos_list

				
				for p in range(base_traces_num): 
					for j in base_endpos_list[p]:
						
						if i+j >= len(base_traces[p]):
							break

						if i+j+1 == len(base_traces[p]):
							is_end = True
						else:
							is_end = False
						
						letter = base_traces[p].vector[i+j]
						atoms = self.genPossibleAtoms(letter, width, dltl.inv, is_end)

						nextdltls = dltl.extenddltl(i, atoms, self.upper_bound, self.operators)

						for nextdltl in nextdltls:
							
							if nextdltl.size >= self.upper_bound:
								continue

							if nextdltl in new_dltl_dict.keys():
								continue

							new_pos_list=[]
							new_neg_list=[]
							c=0

							if nextdltl.vector[-2][0]=='>' and int(nextdltl.vector[-2][1])==i and nextdltl.vector[:-2]+(str(i),nextdltl.vector[-1]) in new_dltl_dict.keys():
								continue

							try:
								
								dummy_dltl = Dltl(nextdltl.vector, 0)
								existing_table = self.R_table[(sl_length, width)][nextdltl]
							except:
								existing_table = None

							for k in range(len(self.sample.positive)):
								
								if pve_endpos_list[k]==[-1]:
									new_pos_list.append([-1])
									continue

								current_superword = self.sample.positive[k]
								last_atom = nextdltl.vector[-1]
								last_digit = int(nextdltl.vector[-2].strip('>'))


								if nextdltl.inv:									
									req_atoms = neg_props(nextdltl.vector[-3])
									last_digit_mod = max(len(current_superword)-last_digit, 0)
									c=0
									for second_last_atom in req_atoms:
										if set(range(len(current_superword)-1,last_digit_mod-1,-1))==\
											set(self.ind_table[(current_superword.vector_str, last_digit_mod, second_last_atom)]):												
												c=1
									
									if c==0:
										new_pos_list.append([-1])
										continue

								new_list = []
								if existing_table:
								  	#count += 1
								  	new_list = existing_table[0][k]
								  	new_pos_list.append(new_list)
								  	continue

								else:

									if pve_endpos_list[k]!=[]:
										#Manually eliminating formulas with last in case of formulas with G
										
										#if dltl.vector==epsilon:
										#	last_digit+=1

										if nextdltl.vector[-2][0]=='>':
											
											next_pos = pve_endpos_list[k][0]+last_digit
											if next_pos <= len(current_superword):
												new_list = self.ind_table[(current_superword.vector_str, next_pos, last_atom)] 
											else:
												new_list = []
										else:

											new_list= [m+last_digit for m in pve_endpos_list[k] \
														if m+last_digit < len(current_superword) and is_sat(current_superword.vector[m+last_digit],last_atom, (m+last_digit)==len(current_superword)-1)]

									new_pos_list.append(new_list)

							
							for k in range(len(self.sample.negative)):

								if nve_endpos_list[k]==[-1]:
									new_neg_list.append([-1])
									continue
								
								current_superword= self.sample.negative[k]
								last_atom = nextdltl.vector[-1]
								last_digit = int(nextdltl.vector[-2].strip('>'))

								#Manually eliminating formulas with last in case of formulas with G

								if nextdltl.inv:
																
									req_atoms = neg_props(nextdltl.vector[-3])
									last_digit_mod = max(len(current_superword)-last_digit, 0)
									c=0
									for second_last_atom in req_atoms:
										if set(range(len(current_superword)-1,last_digit_mod-1,-1))==\
											set(self.ind_table[(current_superword.vector_str, last_digit_mod, second_last_atom)]):												
												c=1
									if c==0:
										new_neg_list.append([-1])
										continue


								new_list=[]
								if existing_table:
									#count += 1
									new_list = existing_table[1][k]
									new_neg_list.append(new_list)
									continue

								else:
									if nve_endpos_list[k]!=[]:
										if nextdltl.vector[-2][0]=='>':
											next_pos = nve_endpos_list[k][0]+last_digit

											if next_pos <= len(current_superword):
												new_list= self.ind_table[(current_superword.vector_str, next_pos, last_atom)] 
											else:
												new_list= []

										else:
											new_list=[m+last_digit for m in nve_endpos_list[k]\
													 if m+last_digit < len(current_superword) and is_sat(current_superword.vector[m+last_digit],last_atom, (m+last_digit)==len(current_superword)-1)]
												
									new_neg_list.append(new_list)



							new_dltl_dict[nextdltl]=(new_pos_list,new_neg_list)
							self.dltlCoverSet(nextdltl, new_pos_list, new_neg_list, sl_length, width)

							try:
								self.len_dltl[(sl_length, width)][nextdltl.size].append(nextdltl)
							except:
								self.len_dltl[(sl_length, width)][nextdltl.size] = [nextdltl]


		self.R_table[(sl_length,width)]=new_dltl_dict


		for length in dltl_lengths:

			if length >= self.upper_bound:

				for dltl in self.len_dltl[(sl_length-1,width)][length]:
					del self.R_table[(sl_length-1,width)][dltl]
				del self.len_dltl[(sl_length-1,width)][length]

		return new_dltl_dict



	def incrWidth(self, sl_length, width):
		''' 
		Width increasing algortihm for finding dltls
		''' 
		
		self.R_table[(sl_length,width)]={} 
		self.len_dltl[(sl_length, width)] = {}

		dltl_lengths = sorted(list(self.len_dltl[(sl_length,1)]))

		for length in dltl_lengths:

			if length >= self.upper_bound:

				for dltl in self.len_dltl[(sl_length,1)][length]:
					del self.R_table[(sl_length,1)][dltl] 
				del self.len_dltl[(sl_length,1)][length]


		dltl_lengths = sorted(list(self.len_dltl[(sl_length,width-1)]))

		for length in dltl_lengths:

			if length >= self.upper_bound:

				for dltl in self.len_dltl[(sl_length,width-1)][length]:
					del self.R_table[(sl_length,width-1)][dltl] 
				del self.len_dltl[(sl_length,width-1)][length]

		dltl_lengths = sorted(list(self.len_dltl[(sl_length,width-1)]))

		for length in dltl_lengths:
		
			for dltl in self.len_dltl[(sl_length, width-1)][length]:
				min_w1_length = length - sum(len_atom(atom,dltl.inv) for atom in dltl.vector[1::2]) + sl_length
				max_w1_length = min_w1_length + sl_length

				for w1_length in range(min_w1_length, max_w1_length+1):

					try:
						self.len_dltl[(sl_length,1)][w1_length]
					except:
						continue

					for w1_dltl in self.len_dltl[(sl_length,1)][w1_length]:
						if w1_dltl.inv != dltl.inv:
							continue

						nextdltl = self.add2dltl(dltl, w1_dltl)
						if nextdltl==None or nextdltl in self.R_table[(sl_length, width)]:
							continue

						else:
							new_pos_list = []
							new_neg_list = []
							old_pos_list1 = self.R_table[(sl_length,width-1)][dltl][0]
							old_pos_list2 = self.R_table[(sl_length,1)][w1_dltl][0]
							old_neg_list1 = self.R_table[(sl_length,width-1)][dltl][1]
							old_neg_list2 = self.R_table[(sl_length,1)][w1_dltl][1]

							for i in range(len(old_pos_list1)):
								if dltl.inv:
									if old_pos_list1==[-1] or old_pos_list2==[-1]:
										new_pos_list.append([-1]) 
									else:
										new_list= sorted(list(set(old_pos_list1[i]).intersection(set(old_pos_list2[i]))))
										new_pos_list.append(new_list)
								else:
									new_list= sorted(list(set(old_pos_list1[i]).intersection(set(old_pos_list2[i]))))
									new_pos_list.append(new_list)
								
							for i in range(len(old_neg_list1)):

								if dltl.inv:
									if old_neg_list1==[-1] or old_neg_list2==[-1]:
										new_neg_list.append([-1]) 
									else:
										new_list= sorted(list(set(old_neg_list1[i]).intersection(set(old_neg_list2[i]))))
										new_neg_list.append(new_list)
								else:
									new_list= sorted(list(set(old_neg_list1[i]).intersection(set(old_neg_list2[i]))))
									new_neg_list.append(new_list)

							self.R_table[(sl_length,width)][nextdltl]=(new_pos_list,new_neg_list)
							self.dltlCoverSet(nextdltl, new_pos_list, new_neg_list, sl_length, width)

							try:
								self.len_dltl[(sl_length, width)][nextdltl.size].append(nextdltl)
							except:
								self.len_dltl[(sl_length, width)][nextdltl.size] = [nextdltl]

		return self.R_table[(sl_length,width)]

	
	def R(self, sl_length, width):
		'''
		Stores the set of satisfying traces for dltls of fixed length and width
		'''
		
		if sl_length > self.max_positive_length:
			raise Exception("Wrong length")

		if width > len(self.sample.positive[0].vector[0])+1:
			raise Exception("Wrong width")

		if sl_length==1 and width==1:
			
			self.len_dltl[(1,1)] = {}
			
			dltl_dict={}
			pve_endpos_list= [[0]]*self.num_positives
			nve_endpos_list= [[0]]*self.num_negatives
			
			empty = Dltl(epsilon, 0)
			empty.size = -1
			
			empty_inv = Dltl(epsilon, 1)
			empty_inv.size = -1

			m = max(self.max_positive_length, self.max_negative_length)

			for i in range(0,m):
				
				for inv in [0,1]:
					
					if inv:
						base_traces = self.sample.negative
						base_traces_num = self.num_negatives
						base_empty = empty_inv
					else:
						base_traces = self.sample.positive
						base_traces_num = self.num_positives
						base_empty = empty

					for p in range(base_traces_num):
						
						if i >= len(base_traces[p]):
							continue

						if i+1 == len(base_traces[p]):
							is_end = True
						else:
							is_end = False
						
						letter = base_traces[p].vector[i]

						atoms = self.genPossibleAtoms(letter, width, inv, is_end)
						nextdltls = base_empty.extenddltl(i, atoms, self.upper_bound, self.operators)
						
						for nextdltl in nextdltls:

							if nextdltl in dltl_dict.keys():
								continue

							if nextdltl.size >= self.upper_bound:
								continue

							pos_list=[]
							neg_list=[]
							c=0

							if nextdltl.vector[-2][0]=='>' and int(nextdltl.vector[-2][1])==i \
									and nextdltl.vector[:-2]+(str(i),nextdltl.vector[-1]) in dltl_dict.keys():
								continue


							for k in range(len(self.sample.positive)):
								
								current_superword = self.sample.positive[k]
								last_atom = nextdltl.vector[-1]
								last_digit = int(nextdltl.vector[-2].strip('>'))

								if inv:
									if len(current_superword)<=last_digit:
										pos_list.append([-1])
										continue

								if nextdltl.vector[0][0]=='>':

									next_pos = pve_endpos_list[k][0]+last_digit#enough to look at ind from the first occurance of nextposword 
									if next_pos <= len(current_superword):
										new_list = self.ind_table[current_superword.vector_str, next_pos, last_atom]
									else:
										new_list= []
								else:
									new_list= [m+last_digit for m in pve_endpos_list[k] if m+last_digit < len(current_superword) and is_sat(current_superword.vector[m+last_digit],last_atom, m+last_digit==len(current_superword)-1)]
								
								pos_list.append(new_list)
						
									
							for k in range(len(self.sample.negative)):
							
								current_superword= self.sample.negative[k]
								last_atom= nextdltl.vector[-1]
								last_digit = int(nextdltl.vector[-2].strip('>'))

								if inv:								
									if len(current_superword)<=last_digit:
										neg_list.append([-1])
										continue

								if nextdltl.vector[0][0]=='>':
									next_pos = nve_endpos_list[k][0]+last_digit
									if next_pos <= len(current_superword):
										new_list= self.ind_table[(current_superword.vector_str, next_pos, last_atom)] 
									else:
										new_list= []
								else:

									new_list=[m+last_digit for m in nve_endpos_list[k] if m+last_digit < len(current_superword) and is_sat(current_superword.vector[m+last_digit],last_atom, m+last_digit==len(current_superword)-1)]
										
								neg_list.append(new_list)
		
							dltl_dict[nextdltl]=(pos_list,neg_list)

							try:
								self.len_dltl[(1,1)][nextdltl.size].append(nextdltl)
							except:
								self.len_dltl[(1,1)][nextdltl.size] = [nextdltl]

							self.dltlCoverSet(nextdltl, pos_list, neg_list, sl_length, width)


			
			self.R_table[(1,1)]=dltl_dict
			return self.R_table[(1,1)]
		
		else:

			try:
				return self.incrLength(sl_length, width)
			except:
				return self.incrWidth(sl_length, width)


	def dltlCoverSet(self, dltl, pos_list, neg_list, sl_length, width):
		'''
		Calculates friend sets from the R-table i.e. the set of satisfying traces from the positive and the negative ones
		'''
		
		if dltl.inv:
			pos_friend_set = {i for i in range(self.num_positives) if pos_list[i]==[]}
			neg_friend_set = {self.num_positives+i for i in range(self.num_negatives) if neg_list[i]==[]}
			
			self.cover_set[(sl_length,width)][dltl] = (pos_friend_set, neg_friend_set)
			cover_size = len(pos_friend_set) - len(neg_friend_set) + len(self.negative_set)
			if cover_size >= self.full_cover*(1-self.thres):
				self.cover_set[(sl_length, width)] = {dltl:(pos_friend_set, neg_friend_set)}
				self.upper_bound = dltl.size
				self.dltl_found = 1
				logging.info("Already Found from dltl of size %d"%(self.upper_bound))

		else:

			pos_friend_set = {i for i in range(self.num_positives) if pos_list[i]!=[]}
			neg_friend_set = {self.num_positives+i for i in range(self.num_negatives) if neg_list[i]!=[]}
			
			# else:
			self.cover_set[(sl_length, width)][dltl] = (pos_friend_set, neg_friend_set)
			cover_size = len(pos_friend_set) - len(neg_friend_set) + len(self.negative_set)
			
			if cover_size >= self.full_cover*(1-self.thres): #checks if it covers the sample w.r.t. the threshold of noise

				self.cover_set[(sl_length, width)] = {dltl:(pos_friend_set, neg_friend_set)}
				self.upper_bound = dltl.size
				self.dltl_found = 1
				logging.info("Already Found from dltl of size %d"%(self.upper_bound))



	def enumerate(self, sl_length, width):

		self.dltl_found = 0
		self.cover_set[(sl_length,width)] = {}
		self.R(sl_length, width)

		