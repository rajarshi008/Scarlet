# if you choose DT learner, you cannot switch off any of the following operators: &, |, !
from formulaTree import Formula


class DTlearner:

	def __init__(self, sample, operators):

		self.sample =  sample
		self.positive_set = {i for i in range(len(self.sample.positive))}
		self.negative_set = {len(self.positive_set)+i for i in range(len(self.sample.negative))}
		self.formula_dict = {}
		self.full_set = (self.positive_set, self.negative_set)
		self.operators = operators 
		assert('&' in self.operators and '|' in self.operators and '!' in self.operators)

	def find(self, upper_bound):
		formula = self.learn((self.positive_set,self.negative_set), self.formula_dict, upper_bound)
		if formula != None:
			return formula, formula.treeSize()
		else:
			return None, upper_bound

	def score_local(self, formula, current_formula):

		return (self.cover_size[formula]-self.cover_size[current_formula])/((formula.treeSize())**(0.5)+1)
	

	def learn(self, sample_set, cover_dict, upper_bound):

		# if sample contains only positive elements
		all_traces = sample_set[0].union(sample_set[1])

		if all_traces.issubset(self.positive_set):
			return Formula('true')
		if all_traces.issubset(self.negative_set):
			return Formula('false')

		while True:
			score = 0
			for formula in cover_dict:
				formula_score = (len(cover_dict[formula][0])-len(cover_dict[formula][1])+len(sample_set))/formula.treeSize()
				if formula_score>score:
					best_formula = formula
					score = formula_score

			if best_formula.treeSize() > upper_bound or cover_dict == {}:
				return None

			split1_set = (cover_dict[best_formula][0], cover_dict[best_formula][1])
			split2_set = (sample_set[0].difference(split1_set[0]), sample_set[1].difference(split1_set[1]) )
		
			if (split1_set[0] == set() and split1_set[1] == set()) or (split2_set[0] == set() and split2_set[1] == set()):
				del(cover_dict[best_formula])
				continue
			else:
				break


		cover_dict1 = {}
		cover_dict2 = {}

		for formula in cover_dict:
			cover_dict1[formula] = (cover_dict[formula][0].difference(split2_set[0]), cover_dict[formula][1].difference(split2_set[1]))
			cover_dict2[formula] = (cover_dict[formula][0].difference(split1_set[0]), cover_dict[formula][1].difference(split1_set[1]))

		formula1 = self.learn(split1_set, cover_dict1, upper_bound-best_formula.treeSize()-1)
		formula2 = self.learn(split2_set, cover_dict2, upper_bound-best_formula.treeSize()-1) # can furthur reduce the size of this tree

		if formula1 == None or formula2 == None:
			return None

		print(best_formula, formula1, formula2)
		if formula1 == Formula('true'):
			first_disjunct = best_formula
		elif formula1 == Formula('false'):
			first_disjunct = None
		else:
			first_disjunct = Formula(['&', best_formula, formula1])

		if formula2 == Formula('true'):
			second_disjunct = best_formula
		elif formula2 == Formula('false'):
			second_disjunct = None
		else:
			second_disjunct = Formula(['&', Formula(['!', best_formula]), formula2])


		if first_disjunct != None and second_disjunct != None:
			final_formula = Formula(['|', first_disjunct, second_disjunct])	
		elif first_disjunct == None:
			final_formula = second_disjunct
		elif second_disjunct == None:
			final_formula = first_disjunct

		print(best_formula, formula1, formula2)

		if final_formula.treeSize() > upper_bound:
			return None
		else:
			return final_formula
		

