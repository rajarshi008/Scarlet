from sample import Sample, Trace
from formulaTree import Formula
import heapq as hq
import time
from booleanSetCover import BooleanSetCover
import logging



epsilon=tuple()
inf_pos = 'end'
len_atom_table = {}

'''
#POSSIBLE OPTIMIZATIONS:
reduce formula size after finding a covering formula
checking to several formulas of high length and width, can reduce that
'''

'''
- We read words from samples as 1,0,0;1,0,1;0,1,1. 
- We say each part of the word as letter, e.g. 1,0,0 
- 0->p, 1->q, 2 -> r,... are the propositions
- (0, ), (1,2) are atoms. (1,2) is an atom of width 2 which means q&R.
'''


#creates the dual atom
def neg_props(atom: tuple)-> list:
	neg_props = [] 
	for i in atom:
		if i[0]=='+':
			neg_props.append(('-'+i[1:],))
		else:
			neg_props.append(('+'+i[1:],))
	return neg_props


def len_atom(atom: tuple, inv: bool)->int:
	try:
		return len_atom_table[(atom, inv)]
	except:
		if inv:
			len_atom_table[(atom, inv)] = 2*len(atom)+len([1 for i in atom if i[0]=='+'])-1
			return len_atom_table[(atom, inv)]
		else:
			len_atom_table[(atom, inv)] = 2*len(atom)+len([1 for i in atom if i[0]=='-'])-1
			return len_atom_table[(atom, inv)]


#Satisfiability of an atom in a letter, e.g. (0,) and (2,) is true in (1,0,1) but (1,) is not
def is_sat(letter:tuple, atom:tuple, is_end: bool) -> bool:

	#check if the propositions in the atom are true in the letter
	
	for pos in atom:
		if pos == '+-1' and not is_end:
			return False
		elif pos == '--1' and is_end:
			return False
		elif pos != '+-1' and pos != '--1':
			if letter[int(pos[1:])] == (pos[0]!='+'):
				return False
	return True


class iSubsequence:

	def __init__(self, vector, inv):
		self.vector = vector
		self.inv = inv

	def __eq__(self, other):
		if other == None:
			return False
		else:
			return (self.vector == other.vector) and (self.inv == other.inv)

	def __ne__(self, other):
		return not self == other

	def __hash__(self):

		return hash((self.vector,self.inv))


	def extendiSubseq(self, diff: int, atoms: tuple, upper_bound: int, operators=['F','G','X','&','|','!']):
		'''
		Given a iSubseq of given width ending at a position and a diff and a letter appearing at position + diff, it outputs all possible 
		iSubseqs of one more length and same width given the length of the formula derived is less than the self.upper_bound.
		'''
		iSubseq_list = []
		
		#Given difference d, the process of appending >0,>1, ..., >d-1 atoms to the iSubseq
		if 'X' not in operators:
			diff = 0

		if (not self.inv and 'F' in operators) or (self.inv and 'G' in operators):
			for atom in atoms:
				#For eliminating p>0p type iSubseqs
				for i in range(diff):
					if self.vector != epsilon and atom == self.vector[-1] and i==0:
						continue

					#new_iSubseq = iSubseq+('>'+str(i),atom)
					new_iSubseq = iSubsequence(self.vector+('>'+str(i),atom), self.inv)	
					base_len = self.size + 1 + (i+1) + len_atom(atom, self.inv)
					
					if base_len >= upper_bound:
						break
					new_iSubseq.size = base_len
					
					iSubseq_list.append(new_iSubseq)

		#Given difference d, the process of appending >d,=d atoms to the iSubseq
		for atom in atoms:#('+1', '-0')
			if 'X' in operators:
				if self.vector != epsilon or not self.inv:

					new_iSubseq = iSubsequence(self.vector+(str(diff),atom), self.inv)
					base_len = self.size + 1 + diff + len_atom(atom, self.inv)
					if base_len < upper_bound:
						new_iSubseq.size = base_len
						iSubseq_list.append(new_iSubseq)
					
			else:
				if self.vector == epsilon or not self.inv:
					new_iSubseq = iSubsequence(self.vector+('0', atom),self.inv)
					new_iSubseq = len_atom(atom, self.inv)
					iSubseq_list.append(new_iSubseq)
					

			if (not self.inv and 'F' in operators) or (self.inv and 'G' in operators):
				new_iSubseq = iSubsequence(self.vector+('>'+str(diff),atom),self.inv)
				base_len = self.size + 1 + (diff+1) + len_atom(atom, self.inv)
				
				if base_len < upper_bound:
					new_iSubseq.size = base_len
					iSubseq_list.append(new_iSubseq)

		return iSubseq_list




#Defining the class iSubseq (indexed Subsequence)
class findiSubsequence:

	def __init__(self, sample, operators,last):
		
		self.sample = sample 
		self.operators = operators
		self.last=last
		
		self.num_positives = len(self.sample.positive)
		self.num_negatives = len(self.sample.negative)

		self.positive_set = {i for i in range(len(self.sample.positive))}
		self.negative_set = {i for i in range(len(self.sample.negative))}
		self.full_cover = len(self.positive_set) + len(self.negative_set)

		#Value determining if "!" is allowed in the operators
		self.neg = '!' in self.operators
		
		#Calculates the maximum length of the traces
		self.max_positive_length = max([len(trace) for trace in self.sample.positive])
		self.max_negative_length = max([len(trace) for trace in self.sample.negative])

		'''
		Initializing DP tables: 
	 	
	 	-Ind_table: For a (word, position, atom) stores all the positions the atom is satisfied in the word starting from the position (including the position)
		-R_table: For (length, width) stores dictionaries for all the iSubseqs of that length and width along with their end positions in all the words in the sample
		-R_table_inv: R_table for the inv traces
		-letter2atom_table: For (letter, width) stores all the possible atoms of that width that is satisfiable in that letter
		-len_atom_table: Stores length of an atom
		-len_iSubseq: Stores iSubseq for different lengths
		'''
		self.ind_table = {}
		self.R_table = {}
		self.cover_set = {} 

		self.len_iSubseq = {}
		self.letter2atom_table= {}


		#Precomputing the Ind_table for atoms of width 1
		
		self.preComputeInd_init()
 
	#Calculates length of an atom both with inv true and false


	#Calculates all possible atoms of given width satisfiable in a given letter
	def letter2atoms(self, letter:tuple, width:int, inv: bool):
		
		try:
			#checks if it is already calculated and stored
			if self.neg:
				return self.letter2atoms_table[(letter, width, '+-')]
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


	#precomputing the ind_table
	def preComputeInd_init(self):

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


	def add2iSubseq(self, iSubseq1: iSubsequence, iSubseq2: iSubsequence):
		'''
		The function takes two iSubseqs of same length one of width w_1 and another of width 1 and returns a iSubseq of same length with width w_1+1
		'''
		
		#checks if the positions in the iSubseqs are exactly same
		iSubseq_no1 = iSubseq1.vector[0::2]
		iSubseq_no2 = iSubseq2.vector[0::2]
		base_len = iSubseq1.size
		
		if iSubseq_no1 != iSubseq_no2:
			return None
		else:
			#starts creating the new iSubseq
			n_iSubseq = iSubsequence(epsilon, iSubseq1.inv)
			for i in range(len(iSubseq2.vector)):

				#for the positions in between it copies it to the new iSubseq as it is
				if isinstance(iSubseq2.vector[i],str):
					n_iSubseq.vector+=(iSubseq2.vector[i],)
				else:
					#checks if the atom in iSubseq2 is already true in the corresponding atom in iSubseq1
					# for j in iSubseq1[i]:
					# 	if j == iSubseq2[i][0]:
					# 		c=1

					if iSubseq2.vector[i][0] in iSubseq1.vector[i]:
						n_iSubseq.vector+=(iSubseq1.vector[i],)
						continue

					for prop in iSubseq1.vector[i]:#()
						if prop[1:] == iSubseq2.vector[i][0][1:]:#('+0',)
							return None
					
					#takes the union of the corresponding atoms in both the iSubseqs and copy it to the new one
					n_iSubseq.vector+=(tuple(sorted(iSubseq1.vector[i]+iSubseq2.vector[i])),)
					base_len += 1+len_atom(iSubseq2.vector[i], iSubseq1.inv) 

			final_iSubseq = n_iSubseq

			if final_iSubseq.vector == iSubseq1.vector or base_len >= self.upper_bound:
				return None

			final_iSubseq.size = base_len

			return final_iSubseq

	def genSequence(self, iSubseq_lengths):

		seq=[]
		curr_sum = iSubseq_lengths[0]+1
		m = max(self.max_positive_length,self.max_negative_length)

		while curr_sum + 2 < self.upper_bound:
			
			for j in iSubseq_lengths:
				if j >= curr_sum:
					break
				i = curr_sum - j	
				if i >= m:
					continue
				seq.append((j,i))
				
			curr_sum=curr_sum+1
		return seq 



	def lengthPTraces(self, pt_length, width):
		

		iSubseq_dict = self.R_table[(pt_length-1,width)]
		new_iSubseq_dict={}

		self.len_iSubseq[(pt_length, width)] = {}
		iSubseq_lengths = sorted(list(self.len_iSubseq[(pt_length-1,width)]))
		seq = self.genSequence(iSubseq_lengths)

		for (length,i) in seq:
			
			if length+i+2 >= self.upper_bound:
				break

			for iSubseq in self.len_iSubseq[(pt_length-1,width)][length]:
				
				pve_endpos_list = iSubseq_dict[iSubseq][0]
				nve_endpos_list = iSubseq_dict[iSubseq][1]
				
				if iSubseq.inv:
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
						atoms = self.genPossibleAtoms(letter, width, iSubseq.inv, is_end)

						nextiSubseqs = iSubseq.extendiSubseq(i, atoms, self.upper_bound, self.operators)

						for nextiSubseq in nextiSubseqs:
							
							if nextiSubseq.size >= self.upper_bound:
								continue

							if nextiSubseq in new_iSubseq_dict.keys():
								continue

							new_pos_list=[]
							new_neg_list=[]
							c=0

							if nextiSubseq.vector[-2][0]=='>' and int(nextiSubseq.vector[-2][1])==i and nextiSubseq.vector[:-2]+(str(i),nextiSubseq.vector[-1]) in new_iSubseq_dict.keys():
								continue

							try:
								#checking if the positive subsequence is already generated
								dummy_iSubseq = iSubsequence(nextiSubseq.vector, 0)
								existing_table = self.R_table[(pt_length, width)][nextiSubseq]
							except:
								existing_table = None

							for k in range(len(self.sample.positive)):
								
								if pve_endpos_list[k]==[-1]:
									new_pos_list.append([-1])
									continue

								current_superword = self.sample.positive[k]
								last_atom = nextiSubseq.vector[-1]
								last_digit = int(nextiSubseq.vector[-2].strip('>'))


								if nextiSubseq.inv:									
									req_atoms = neg_props(nextiSubseq.vector[-3])
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
										
										#if iSubseq.vector==epsilon:
										#	last_digit+=1

										if nextiSubseq.vector[-2][0]=='>':
											
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
								last_atom = nextiSubseq.vector[-1]
								last_digit = int(nextiSubseq.vector[-2].strip('>'))

								#Manually eliminating formulas with last in case of formulas with G

								if nextiSubseq.inv:
																
									req_atoms = neg_props(nextiSubseq.vector[-3])
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
										if nextiSubseq.vector[-2][0]=='>':
											next_pos = nve_endpos_list[k][0]+last_digit

											if next_pos <= len(current_superword):
												new_list= self.ind_table[(current_superword.vector_str, next_pos, last_atom)] 
											else:
												new_list= []

										else:
											new_list=[m+last_digit for m in nve_endpos_list[k]\
													 if m+last_digit < len(current_superword) and is_sat(current_superword.vector[m+last_digit],last_atom, (m+last_digit)==len(current_superword)-1)]
												
									new_neg_list.append(new_list)



							new_iSubseq_dict[nextiSubseq]=(new_pos_list,new_neg_list)
							self.iSubseqCoverSet(nextiSubseq, new_pos_list, new_neg_list, pt_length, width)

							try:
								self.len_iSubseq[(pt_length, width)][nextiSubseq.size].append(nextiSubseq)
							except:
								self.len_iSubseq[(pt_length, width)][nextiSubseq.size] = [nextiSubseq]


		self.R_table[(pt_length,width)]=new_iSubseq_dict


		for length in iSubseq_lengths:

			if length >= self.upper_bound:

				for iSubseq in self.len_iSubseq[(pt_length-1,width)][length]:
					del self.R_table[(pt_length-1,width)][iSubseq]
				del self.len_iSubseq[(pt_length-1,width)][length]

		return new_iSubseq_dict



	def widthPTraces(self, pt_length, width):

		# if inv:
		# 	base_table = self.R_table_inv
		# else:
		# 	base_table = self.R_table
		
		self.R_table[(pt_length,width)]={} 
		self.len_iSubseq[(pt_length, width)] = {}

		iSubseq_lengths = sorted(list(self.len_iSubseq[(pt_length,1)]))

		for length in iSubseq_lengths:

			if length >= self.upper_bound:

				for iSubseq in self.len_iSubseq[(pt_length,1)][length]:
					del self.R_table[(pt_length,1)][iSubseq] 
				del self.len_iSubseq[(pt_length,1)][length]


		iSubseq_lengths = sorted(list(self.len_iSubseq[(pt_length,width-1)]))

		for length in iSubseq_lengths:

			if length >= self.upper_bound:

				for iSubseq in self.len_iSubseq[(pt_length,1)][length]:
					del self.R_table[(pt_length,width-1)][iSubseq] 
				del self.len_iSubseq[(pt_length,width-1)][length]


		for length in iSubseq_lengths:
		
			for iSubseq in self.len_iSubseq[(pt_length, width-1)][length]:
			#self.R_table[(pt_length,width)][iSubseq]= self.R_table[(pt_length,width-1)][iSubseq]
				min_w1_length = length - sum([len_atom(atom,iSubseq.inv) for atom in iSubseq.vector[1::2]]) + pt_length
				max_w1_length = min_w1_length + pt_length

				for w1_length in range(min_w1_length, max_w1_length+1):

					try:
						self.len_iSubseq[(pt_length,1)][w1_length]
					except:
						continue

					for w1_iSubseq in self.len_iSubseq[(pt_length,1)][w1_length]:
						if w1_iSubseq.inv != iSubseq.inv:
							continue

						nextiSubseq = self.add2iSubseq(iSubseq, w1_iSubseq)
						if nextiSubseq==None or nextiSubseq in self.R_table[(pt_length, width)]:
							continue

						else:
							new_pos_list = []
							new_neg_list = []
							old_pos_list1 = self.R_table[(pt_length,width-1)][iSubseq][0]
							old_pos_list2 = self.R_table[(pt_length,1)][w1_iSubseq][0]
							old_neg_list1 = self.R_table[(pt_length,width-1)][iSubseq][1]
							old_neg_list2 = self.R_table[(pt_length,1)][w1_iSubseq][1]

							for i in range(len(old_pos_list1)):
								if iSubseq.inv:
									if old_pos_list1==[-1] or old_pos_list2==[-1]:
										new_pos_list.append([-1]) 
									else:
										new_list= sorted(list(set(old_pos_list1[i]).intersection(set(old_pos_list2[i]))))
										new_pos_list.append(new_list)
								else:
									new_list= sorted(list(set(old_pos_list1[i]).intersection(set(old_pos_list2[i]))))
									new_pos_list.append(new_list)
								# if new_list== []:
								# 	break_value=1
								# 	break
							# if break_value==1:
								# continue
								
							for i in range(len(old_neg_list1)):

								if iSubseq.inv:
									if old_neg_list1==[-1] or old_neg_list2==[-1]:
										new_neg_list.append([-1]) 
									else:
										new_list= sorted(list(set(old_neg_list1[i]).intersection(set(old_neg_list2[i]))))
										new_neg_list.append(new_list)
								else:
									new_list= sorted(list(set(old_neg_list1[i]).intersection(set(old_neg_list2[i]))))
									new_neg_list.append(new_list)

							self.R_table[(pt_length,width)][nextiSubseq]=(new_pos_list,new_neg_list)
							self.iSubseqCoverSet(nextiSubseq, new_pos_list, new_neg_list, pt_length, width)

							try:
								self.len_iSubseq[(pt_length, width)][nextiSubseq.size].append(nextiSubseq)
							except:
								self.len_iSubseq[(pt_length, width)][nextiSubseq.size] = [nextiSubseq]

		return self.R_table[(pt_length,width)]

	
	def R(self, pt_length, width):
		
		if pt_length > self.max_positive_length:
			raise Exception("Wrong length")

		if width > len(self.sample.positive[0].vector[0])+1:
			raise Exception("Wrong width")

		if pt_length==1 and width==1:
			
			self.len_iSubseq[(1,1)] = {}
			
			iSubseq_dict={}
			pve_endpos_list= [[0]]*self.num_positives
			nve_endpos_list= [[0]]*self.num_negatives
			
			empty = iSubsequence(epsilon, 0)
			empty.size = -1
			
			empty_inv = iSubsequence(epsilon, 1)
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
						nextiSubseqs = base_empty.extendiSubseq(i, atoms, self.upper_bound, self.operators)
						
						for nextiSubseq in nextiSubseqs:

							if nextiSubseq in iSubseq_dict.keys():
								continue

							pos_list=[]
							neg_list=[]
							c=0

							if nextiSubseq.vector[-2][0]=='>' and int(nextiSubseq.vector[-2][1])==i \
									and nextiSubseq.vector[:-2]+(str(i),nextiSubseq.vector[-1]) in iSubseq_dict.keys():
								continue


							for k in range(len(self.sample.positive)):
								
								current_superword= self.sample.positive[k]
								last_atom = nextiSubseq.vector[-1]
								last_digit = int(nextiSubseq.vector[-2].strip('>'))

								if inv:
									if len(current_superword)-1<last_digit:
										new_pos_list.append([-1])
										continue

								if nextiSubseq.vector[0][0]=='>':

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
								last_atom= nextiSubseq.vector[-1]
								last_digit = int(nextiSubseq.vector[-2].strip('>'))

								if inv:								
									if len(current_superword)<last_digit:
										neg_list.append([-1])
										continue

								if nextiSubseq.vector[0][0]=='>':
									next_pos = nve_endpos_list[k][0]+last_digit
									if next_pos <= len(current_superword):
										new_list= self.ind_table[(current_superword.vector_str, next_pos, last_atom)] 
									else:
										new_list= []
								else:

									new_list=[m+last_digit for m in nve_endpos_list[k] if m+last_digit < len(current_superword) and is_sat(current_superword.vector[m+last_digit],last_atom, m+last_digit==len(current_superword)-1)]
										
								neg_list.append(new_list)
		
							iSubseq_dict[nextiSubseq]=(pos_list,neg_list)

							try:
								self.len_iSubseq[(1,1)][nextiSubseq.size].append(nextiSubseq)
							except:
								self.len_iSubseq[(1,1)][nextiSubseq.size] = [nextiSubseq]

							self.iSubseqCoverSet(nextiSubseq, pos_list, neg_list, pt_length, width)


			
			self.R_table[(1,1)]=iSubseq_dict
			return self.R_table[(1,1)]
		
		else:

			try:
				return self.lengthPTraces(pt_length, width)
			except:
				return self.widthPTraces(pt_length, width)


	def iSubseqCoverSet(self, iSubseq, pos_list, neg_list, pt_length, width):


		if iSubseq.inv:
			pos_friend_set = {i for i in range(self.num_positives) if pos_list[i]==[]}
			neg_friend_set = {self.num_positives+i for i in range(self.num_negatives) if neg_list[i]==[]}
			
			self.cover_set[(pt_length,width)][iSubseq] = (pos_friend_set, neg_friend_set)
			cover_size = len(pos_friend_set) - len(neg_friend_set) + len(self.negative_set)
			if cover_size == self.full_cover:
				self.cover_set[(pt_length, width)] = {iSubseq:(pos_friend_set, neg_friend_set)}
				self.upper_bound = iSubseq.size
				self.Subseq_found = 1
				logging.info("Already Found from iSubsequence of size %d"%(self.upper_bound))

		else:

			pos_friend_set = {i for i in range(self.num_positives) if pos_list[i]!=[]}
			neg_friend_set = {self.num_positives+i for i in range(self.num_negatives) if neg_list[i]!=[]}
			
			# else:
			self.cover_set[(pt_length, width)][iSubseq] = (pos_friend_set, neg_friend_set)
			cover_size = len(pos_friend_set) - len(neg_friend_set) + len(self.negative_set)
			if cover_size == self.full_cover:

				self.cover_set[(pt_length, width)] = {iSubseq:(pos_friend_set, neg_friend_set)}
				self.upper_bound = iSubseq.size
				self.Subseq_found = 1
				logging.info("Already Found from iSubsequence of size %d"%(self.upper_bound))



	def enumerate(self, pt_length, width):

		self.Subseq_found = 0
		self.cover_set[(pt_length,width)] = {}
		self.R(pt_length, width)

		'''
		count, count_inv = 0, 0
		for iSubseq in self.R_table[(pt_length, width)]:
			if iSubseq.inv:
				count_inv+=1
			else:
				count+=1

		logging.debug('Found iSubseqs %d and reverse iSubseqs %d'%(count, count_inv))
		'''