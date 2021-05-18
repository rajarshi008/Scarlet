from .sample import Sample, Trace
from .formulaTree import Formula
import heapq as hq
import time
from .booleanSetCover import BooleanSetCover
import logging

#from .booleanSetCover import BooleanSetCover


epsilon=tuple()
inf_pos = 'end'
inf_word = 'omega'

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

'''
Operators: (F, &)
F - length = 1, width=1 no need of adding & and | in booleanSetCover
& - length = min_isubtive_length, width=max_num_propositions, add & in booleanSetCover
'''



#Satisfiability of an atom in a letter, e.g. (0,) and (2,) is true in (1,0,1) but (1,) is not
def neg_props(atom: tuple)-> list:
	neg_props = [] 
	for i in atom:
		if i[0]=='+':
			neg_props.append(('-'+i[1],))
		else:
			neg_props.append(('+'+i[1],))
	return neg_props




def is_sat(letter:tuple, atom:tuple) -> bool:

	#check if the propositions in the atom are true in the letter
	for pos in atom:
		if letter[int(pos[1:])] == (pos[0]!='+'):
			return False
	return True




#Defining the class PosTrace
class iSubTrace:

	def __init__(self, sample, operators):
		
		self.sample = sample 
		self.operators = operators
		self.neg = '!' in self.operators
		self.num_positives = len(self.sample.positive)
		self.num_negatives = len(self.sample.negative)

		#we sort the sample of positive and negative words according to their lengths
		#self.sample.positive = sorted(self.sample.positive, key=lambda x: len(x))
		#self.sample.negative = sorted(self.sample.negative, key=lambda x: len(x))

		#Calculates the length of the shortest positive word
		#self.min_positive_length = min([len(word) for word in self.sample.positive])
		self.max_positive_length = max([len(word) for word in self.sample.positive])
		self.max_negative_length = max([len(word) for word in self.sample.negative])

		#Initializing DP tables: 
		# 	-Ind_table: For a (word, position, atom) stores all the positions the atom is satisfied in the word starting from the position (including the position)
		#	-R_table: For (length, width) stores dictionaries for all the isubtraces of that length and width along with their end positions in all the words in the sample
		#	-letter2atom_table: For (letter, width) stores all the possible atoms of that width that is satisfiable in that letter
		self.ind_table = {}
		self.R_table = {}
		self.R_table_inv = {}

		self.len_isubtrace = {}
		self.letter2atom_table= {}
		self.len_atom_table = {}

		#Precomputing the Ind_table for atoms of all possible widths
		width = len(self.sample.positive[0].vector[0])
		self.preComputeInd(width)
 
	def len_atom(self, atom: tuple, inv: bool)->int:
		try:
			return self.len_atom_table[(atom, inv)]
		except:
			if inv:
				self.len_atom_table[(atom, inv)] = 2*len(atom)+len([1 for i in atom if i[0]=='+'])-1
				return self.len_atom_table[(atom, inv)]
			else:
				self.len_atom_table[(atom, inv)] = 2*len(atom)+len([1 for i in atom if i[0]=='-'])-1
				return self.len_atom_table[(atom, inv)]

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


	
	# Given a isubtrace of given width ending at a position and a diff and a letter appearing at position + diff, it outputs all possible isubtraces of one more length and same width
	# 	given the length of FaXTL from it does not cross the upper_bound.
	
	def possiblePTraces(self, isubtrace:tuple, diff: int, letter: str, width: int, upper_bound: int, inv: bool):
		
		#list of all new isubtraces
		isubtraces_list = []

		#list of atoms of width upto width from letter
		atoms = []
		for i in range(1,width+1):
			atoms+=self.letter2atoms(letter, i, inv)
		
		#Given difference d, the process of appending >0,>1, ..., >d-1 atoms to the isubtrace
		if 'X' not in self.operators:
			diff = 0

		if (not inv and 'F' in self.operators) or (inv and 'G' in self.operators):
			for atom in atoms:
				#For eliminating p>0p type isubtraces
				for i in range(diff):	
					if isubtrace != epsilon and atom == isubtrace[-1] and i==0:
						continue

					new_isubtrace = isubtrace+('>'+str(i),atom)
					
					base_len=self.len_isubtrace[(isubtrace, inv)] + 1 + (i+1) + self.len_atom(atom, inv)
					if base_len >= upper_bound:
						break
					self.len_isubtrace[(new_isubtrace,inv)] = base_len
					
					isubtraces_list.append(new_isubtrace)

		#Given difference d, the process of appending >d,=d atoms to the isubtrace
		for atom in atoms:#('+1', '-0')
			if 'X' in self.operators:
				if isubtrace != epsilon or not inv:
					new_isubtrace = isubtrace+(str(diff),atom)
					base_len = self.len_isubtrace[(isubtrace, inv)] + 1 + (diff) + self.len_atom(atom, inv)
					if base_len < upper_bound:
						self.len_isubtrace[(new_isubtrace, inv)] = base_len
						isubtraces_list.append(new_isubtrace)
					
			else: 
				if isubtrace == epsilon or not inv:
					new_isubtrace = isubtrace+(str(diff),atom)
					self.len_isubtrace[(new_isubtrace, inv)] = self.len_atom(atom,inv)
					isubtraces_list.append(new_isubtrace)
					

			if (not inv and 'F' in self.operators) or (inv and 'G' in self.operators):
				new_isubtrace = isubtrace+('>'+str(diff),atom)
				base_len=self.len_isubtrace[(isubtrace,inv)] + 1 + (diff+1) + self.len_atom(atom, inv)
				
				if base_len < upper_bound:
					self.len_isubtrace[(new_isubtrace,inv)] = base_len
					isubtraces_list.append(new_isubtrace)		
		return isubtraces_list


	#precomputing the ind_table
	def preComputeInd(self, width: int):

		all_atoms={i: set() for i in range(1,width+1)}
		if self.neg:
			for trace in self.sample.positive+self.sample.negative:
				for letter in trace.vector:	
					for i in range(1,width+1):
						all_atoms[i]= all_atoms[i].union(set(self.letter2atoms(letter, i, True)))

		else:
			for trace in self.sample.positive:
				for letter in trace.vector:	
					for i in range(1,width+1):
						all_atoms[i]= all_atoms[i].union(set(self.letter2atoms(letter, i, True)))

			for trace in self.sample.negative:
				for letter in trace.vector:	
					for i in range(1,width+1):
						all_atoms[i]= all_atoms[i].union(set(self.letter2atoms(letter, i, False)))


		for word_vec in self.sample.positive+ self.sample.negative:
				
				word=word_vec.vector_str
				for atom in all_atoms[1]:
					self.ind_table[(word, inf_pos, atom)]=[]
					self.ind_table[(word, len(word_vec), atom)]=[]
					for pos in range(len(word_vec)-1,-1,-1):
						
						if word_vec.vector[pos][int(atom[0][1:])] == (atom[0][0]=='+'):#checking if atom starts with ! implicitly
							self.ind_table[(word, pos, atom)]=[pos]+self.ind_table[(word, pos+1, atom)]
						else:
							self.ind_table[(word, pos, atom)]=self.ind_table[(word, pos+1, atom)]
		
				if width>1:				
					for i in range(2,width+1):
						for atom in all_atoms[i]:
							self.ind_table[(word, inf_pos, atom)]=[]
							self.ind_table[(word, len(word_vec), atom)]=[]
							for pos in range(len(word_vec)):
								set1=set(self.ind_table[(word,pos,(atom[0],))])
								for j in atom[1:]:
									set1=set1.intersection(set(self.ind_table[(word,pos,(j,))]))

								self.ind_table[(word, pos, atom)]=list(set1)


	def add2isubtrace(self, isubtrace1:tuple, isubtrace2:tuple, inv: bool, upper_bound: int):
		'''
		The function takes two isubtraces of same length one of width w_1 and another of width 1 and returns a isubtrace of same length with width w_1+1
		'''
		
		#checks if the positions in the isubtraces are exactly same
		isubtrace_no1= isubtrace1[0::2]
		isubtrace_no2= isubtrace2[0::2]
		base_len=self.len_isubtrace[(isubtrace1,inv)]
		
		if isubtrace_no1 != isubtrace_no2:
			return None
		else:
			#starts creating the new isubtrace
			n_isubtrace=[]
			for i in range(len(isubtrace2)):

				#for the positions in between it copies it to the new isubtrace as it is
				if isinstance(isubtrace2[i],str):
					n_isubtrace.append(isubtrace2[i])
				else:
					#checks if the atom in isubtrace2 is already true in the corresponding atom in isubtrace1
					# for j in isubtrace1[i]:
					# 	if j == isubtrace2[i][0]:
					# 		c=1

					if isubtrace2[i][0] in isubtrace1[i]:
						n_isubtrace.append(isubtrace1[i])
						continue

					for prop in isubtrace1[i]:
						if prop[1:] == isubtrace2[i][0][1:]:
							return None
					
					#takes the union of the corresponding atoms in both the isubtraces and copy it to the new one
					n_isubtrace.append(tuple(sorted(isubtrace1[i]+isubtrace2[i])))
					base_len += 1+self.len_atom(isubtrace2[i], inv) 

			final_isubtrace = tuple(n_isubtrace)

			if final_isubtrace == isubtrace1 or base_len > upper_bound:
				return None

			self.len_isubtrace[(final_isubtrace,inv)] = base_len

			
			return final_isubtrace

	def lengthPTraces(self, pt_length, width, upper_bound, inv):


		deleted_isubtraces = []
		if inv:
			base_table = self.R_table_inv
			base_traces = self.sample.negative
			base_traces_num = self.num_negatives
		else:
			base_table = self.R_table
			base_traces = self.sample.positive
			base_traces_num = self.num_positives


		for isubtrace in base_table[(pt_length-1,width)].keys():
			if self.len_isubtrace[(isubtrace,inv)] >= upper_bound:
				deleted_isubtraces.append(isubtrace)
		
		for isubtrace in deleted_isubtraces:
			del base_table[(pt_length-1,width)][isubtrace]

		isubtrace_dict= base_table[(pt_length-1,width)]
		new_isubtrace_dict={}
		count = 0
		for isubtrace in isubtrace_dict.keys():
			
			pve_endpos_list = isubtrace_dict[isubtrace][0]
			nve_endpos_list = isubtrace_dict[isubtrace][1]
				
			if inv:
				base_endpos_list = nve_endpos_list	
			else:
				base_endpos_list = pve_endpos_list

			
			for p in range(base_traces_num): 
				for j in base_endpos_list[p]:#-

					for i in range(1,len(base_traces[p])-j):
						letter = base_traces[p].vector[i+j]
						nextisubtraces = self.possiblePTraces(isubtrace, i, letter, width, upper_bound, inv)
						for nextisubtrace in nextisubtraces:
							
							if nextisubtrace in new_isubtrace_dict.keys():
								continue
							new_pos_list=[]
							new_neg_list=[]
							c=0

							if nextisubtrace[-2][0]=='>' and int(nextisubtrace[-2][1])==i and nextisubtrace[:-2]+(str(i),nextisubtrace[-1]) in new_isubtrace_dict.keys():
								continue

							try:
							 	existing_table = self.R_table[(pt_length, width)][nextisubtrace]
							except:
							 	existing_table = None


							for k in range(len(self.sample.positive)):
								
								if pve_endpos_list[k]==[-1]:
									new_pos_list.append([-1])
									continue

								current_superword= self.sample.positive[k]
								last_atom = nextisubtrace[-1]
								last_digit = int(nextisubtrace[-2].strip('>'))


								if inv:									
									req_atoms = neg_props(nextisubtrace[-3])
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
								  	count += 1
								  	new_list = existing_table[0][k]
								  	new_pos_list.append(new_list)
								  	continue

								else:

									if pve_endpos_list[k]!=[]:	
										#Manually eliminating formulas with last in case of formulas with G
										
										if isubtrace==epsilon:
											last_digit+=1

										if nextisubtrace[-2][0]=='>':
											
											next_pos = pve_endpos_list[k][0]+last_digit
											if next_pos <= len(current_superword):
												new_list= self.ind_table[(current_superword.vector_str, next_pos, last_atom)] 
											else:
												new_list= []
										else:
											new_list= [m+last_digit for m in pve_endpos_list[k] \
														if m+last_digit < len(current_superword) and is_sat(current_superword.vector[m+last_digit],last_atom)]

									new_pos_list.append(new_list)

							
							for k in range(len(self.sample.negative)):

								if nve_endpos_list[k]==[-1]:
									new_neg_list.append([-1])
									continue
								
								current_superword= self.sample.negative[k]
								last_atom = nextisubtrace[-1]
								last_digit = int(nextisubtrace[-2].strip('>'))

								#Manually eliminating formulas with last in case of formulas with G
								
								if inv:
																
									req_atoms = neg_props(nextisubtrace[-3])
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
									count += 1
									new_list = existing_table[1][k]
									new_neg_list.append(new_list)
									continue

								else:
									if nve_endpos_list[k]!=[]:
										if nextisubtrace[-2][0]=='>':
											next_pos = nve_endpos_list[k][0]+last_digit
											if next_pos <= len(current_superword):
												new_list= self.ind_table[(current_superword.vector_str, next_pos, last_atom)] 
											else:
												new_list= []
										else:
											new_list=[m+last_digit for m in nve_endpos_list[k]\
													 if m+last_digit < len(current_superword) and is_sat(current_superword.vector[m+last_digit],last_atom)]
												
									new_neg_list.append(new_list)

								
							new_isubtrace_dict[nextisubtrace]=(new_pos_list,new_neg_list)
		base_table[(pt_length,width)]=new_isubtrace_dict

		return new_isubtrace_dict



	def widthPTraces(self, pt_length, width, upper_bound, inv):

		if inv:
			base_table = self.R_table_inv
		else:
			base_table = self.R_table
		
		base_table[(pt_length,width)]={} 
		
		deleted_isubtraces= []
		for isubtrace in base_table[(pt_length, width-1)].keys():
			if self.len_isubtrace[(isubtrace,inv)]>= upper_bound:
				deleted_isubtraces.append(isubtrace)

		for isubtrace in deleted_isubtraces:
			del base_table[(pt_length,width-1)][isubtrace]
		
		for isubtrace in base_table[(pt_length,width-1)].keys():

			#self.R_table[(pt_length,width)][isubtrace]= self.R_table[(pt_length,width-1)][isubtrace]

			for w1_isubtrace in base_table[(pt_length,1)]:
				nextisubtrace = self.add2isubtrace(isubtrace, w1_isubtrace, inv, upper_bound)
				if nextisubtrace==None or nextisubtrace in base_table[(pt_length, width)]:
					continue

				else:
					new_pos_list = []
					new_neg_list = []
					old_pos_list1 = base_table[(pt_length,width-1)][isubtrace][0]
					old_pos_list2 = base_table[(pt_length,1)][w1_isubtrace][0]
					old_neg_list1 = base_table[(pt_length,width-1)][isubtrace][1]
					old_neg_list2 = base_table[(pt_length,1)][w1_isubtrace][1]

					for i in range(len(old_pos_list1)):
						if inv:
							if old_pos_list1==[-1] or old_pos_list2==[-1]:
								new_pos_list.append([-1]) 
							else:
								new_list= list(set(old_pos_list1[i]).intersection(set(old_pos_list2[i])))
								new_pos_list.append(new_list)
						else:
							new_list= list(set(old_pos_list1[i]).intersection(set(old_pos_list2[i])))
							new_pos_list.append(new_list)
						# if new_list== []:
						# 	break_value=1
						# 	break
					# if break_value==1:
						# continue
						
					for i in range(len(old_neg_list1)):

						if inv:
							if old_neg_list1==[-1] or old_neg_list2==[-1]:
								new_neg_list.append([-1]) 
							else:
								new_list= list(set(old_neg_list1[i]).intersection(set(old_neg_list2[i])))
								new_neg_list.append(new_list)
						else:
							new_list= list(set(old_neg_list1[i]).intersection(set(old_neg_list2[i])))
							new_neg_list.append(new_list)

					base_table[(pt_length,width)][nextisubtrace]=(new_pos_list,new_neg_list)

		return base_table[(pt_length,width)]

	
	def R(self, pt_length, width, upper_bound, inv):
		
		if pt_length > self.max_positive_length:
			raise Exception("Wrong length")

		if width > len(self.sample.positive[0].vector[0]):
			raise Exception("Wrong width")

		if pt_length==1 and width==1:
			new_isubtrace_dict={}
			pve_endpos_list= [[0]]*self.num_positives
			nve_endpos_list= [[0]]*self.num_negatives
			self.len_isubtrace[(epsilon,inv)] = -1

			if inv:
				base_traces = self.sample.negative
				base_traces_num = self.num_negatives
			else:
				base_traces = self.sample.positive
				base_traces_num = self.num_positives 


			for p in range(base_traces_num):
				for i in range(0,len(base_traces[p])):

					letter = base_traces[p].vector[i]
					nextisubtraces = self.possiblePTraces(epsilon, i, letter, width, upper_bound, inv)
					for nextisubtrace in nextisubtraces:
						if nextisubtrace in new_isubtrace_dict.keys():
							continue
						new_pos_list=[]
						new_neg_list=[]
						c=0

						if nextisubtrace[-2][0]=='>' and int(nextisubtrace[-2][1])==i \
								and nextisubtrace[:-2]+(str(i),nextisubtrace[-1]) in new_isubtrace_dict.keys():
							continue


						for k in range(len(self.sample.positive)):
							
							current_superword= self.sample.positive[k]
							last_atom = nextisubtrace[-1]
							last_digit = int(nextisubtrace[-2].strip('>'))

							if inv:
								if len(current_superword)<last_digit:
									new_pos_list.append([-1])

									continue

							if nextisubtrace[0][0]=='>':

								next_pos = pve_endpos_list[k][0]+last_digit#enough to look at ind from the first occurance of nextposword 
								if next_pos <= len(current_superword):
									new_list = self.ind_table[current_superword.vector_str, next_pos, last_atom]
								else:
									new_list= []
							else:
								new_list= [m+last_digit for m in pve_endpos_list[k] if m+last_digit < len(current_superword) and is_sat(current_superword.vector[m+last_digit],last_atom)]
							
							new_pos_list.append(new_list)
					
								
						for k in range(len(self.sample.negative)):
						
							current_superword= self.sample.negative[k]
							last_atom= nextisubtrace[-1]
							last_digit = int(nextisubtrace[-2].strip('>'))

							if inv:								
								if len(current_superword)<last_digit:
									new_neg_list.append([-1])
									continue

							if nextisubtrace[0][0]=='>':
								next_pos = nve_endpos_list[k][0]+last_digit
								if next_pos <= len(current_superword):
									new_list= self.ind_table[(current_superword.vector_str, next_pos, last_atom)] 
								else:
									new_list= []
							else:

								new_list=[m+last_digit for m in nve_endpos_list[k] if m+last_digit < len(current_superword) and is_sat(current_superword.vector[m+last_digit],last_atom)]
									
							new_neg_list.append(new_list)

								
							new_isubtrace_dict[nextisubtrace]=(new_pos_list,new_neg_list)
			
			if inv:
				self.R_table_inv[(1,1)]=new_isubtrace_dict
				return self.R_table_inv[(1,1)]
			else:
				self.R_table[(1,1)]=new_isubtrace_dict
				return self.R_table[(1,1)]
		else:
			try:
				return self.lengthPTraces(pt_length, width, upper_bound, inv)
			except:
				return self.widthPTraces(pt_length, width, upper_bound, inv)


	def coverSet(self, pt_length, width, upper_bound):
		
		isubtrace_dict = {}
		isubtrace_dict_inv = {}

		if pt_length <= self.max_positive_length: 
			
			if ('&' not in self.operators and pt_length==1 and width==1) or ('&' in self.operators):
				isubtrace_dict = self.R(pt_length, width, upper_bound, inv=False)

		if pt_length <= self.max_negative_length:

			if ('|' not in self.operators and pt_length==1 and width==1) or ('|' in self.operators):
				isubtrace_dict_inv = self.R(pt_length, width, upper_bound, inv=True)

		logging.debug('Found isubtraces %d and reverse isubtraces %d'%(len(isubtrace_dict), len(isubtrace_dict_inv)))


		if pt_length==1 and width==1:
			print(isubtrace_dict[('0',('+1',))])

		# if pt_length==2 and width==1:
		# 	print(isubtrace_dict[('>0', ('+0',), '>0', ('+1',))])

		cover_set = {}
		#victims_full = {}
		#case=0
		for isubtrace in isubtrace_dict.keys():

			pos_friend_set = {i for i in range(self.num_positives) if isubtrace_dict[isubtrace][0][i]!=[]}
			neg_friend_set = {i for i in range(self.num_negatives) if isubtrace_dict[isubtrace][1][i]!=[]}
			#Not sure about this, can put this if necessary
			# if len(victim_set) == self.num_negatives:
			# 	case=1
			# 	victims_full[isubtrace]=(victim_set, len(victim_set))

			# else:
			cover_set[isubtrace] = (pos_friend_set, neg_friend_set)
			
		for isubtrace in isubtrace_dict_inv.keys():

			pos_friend_set = {i for i in range(self.num_positives) if isubtrace_dict_inv[isubtrace][0][i]==[]}
			neg_friend_set = {i for i in range(self.num_negatives) if isubtrace_dict_inv[isubtrace][1][i]==[]}
			

			cover_set[('!',)+isubtrace] = (pos_friend_set, neg_friend_set)
		#if case==1:
		#	victims = victims_full

		return cover_set

	
	#Finding the shortest isubtrace	

