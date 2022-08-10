import logging
import os
from graphviz import Source
from Scarlet.formulaTree import *


#The decision tree algorithm for combinations of dLTLS
class DecisionTree:

	def __init__(self, label, thres, leftChild=None, rightChild=None):

		assert(label != None)
		assert(type(label)==Formula)
		self.label = label
		self.left = leftChild
		self.right = rightChild
		self.thres = thres
		self.size = None

	def DTSize(self):
		'''
			calculates decision tree size
		''' 
		
		leftSize = 0
		rightSize = 0

		if self.left != None:
			if self.left.label != formula_true and self.left.label != formula_false:
				leftSize = 1 + self.left.DTSize()
		if self.right != None:
			if self.right.label != formula_true and self.right.label != formula_false:
				rightSize = 1 + self.right.DTSize()

		self.size = self.label.treeSize() + leftSize + rightSize  
		return self.size

	def generate_dot(self):
		'''
			generates dot files for the tree  
		'''
		tree_queue = [(self,1)]
		tree_id = {1: self}
		edges = []

		while tree_queue != []:

			curr_tree, curr_id = tree_queue.pop()

			if curr_tree.left != None:
				left_id = 2*curr_id 
				tree_queue.insert(0,(curr_tree.left,left_id))
				tree_id[left_id] = curr_tree.left
				edges.append((curr_id,left_id,0))
			
			if curr_tree.right != None:
				right_id = 2*curr_id+1
				tree_queue.insert(0,(curr_tree.right, right_id))
				tree_id[right_id] = curr_tree.right
				edges.append((curr_id,right_id,1))

		dot_str =  "digraph g {\n"

		for i in tree_id:
			dot_str += ('{} [label="{}"]\n'.format(i, tree_id[i].label))
		for edge in edges:
			if edge[2]:
				dot_str += ('{} -> {}\n [style= {}]'.format(edge[0],edge[1],'dashed'))
			else:
				dot_str += ('{} -> {}\n [style= {}]'.format(edge[0],edge[1],'solid'))

		dot_str += ("}\n")
		
		return dot_str

	def save(self, filename):

		dot_str = self.generate_dot()
		s = Source(dot_str, filename=filename, format="png")

	def show(self):

		dot_str = self.generate_dot()
		s = Source(dot_str, filename='test.gv', format="png")
		s.view()

	def convert2LTL(self):
		'''
			returns the LTL equivalent of the DT
		'''
		if self.label == formula_true or self.label== formula_false:
			return self.label

		if self.left.label == Formula('true'):
			first_disjunct = self.label
		elif self.left.label == Formula('false'):
			first_disjunct = None
		else:
			first_disjunct = Formula(['&', self.label, self.left.convert2LTL()])

		if self.right.label == Formula('true'):
			second_disjunct = self.label
		elif self.right.label == Formula('false'):
			second_disjunct = None
		else:
			second_disjunct = Formula(['&', Formula(['!', self.label]), self.right.convert2LTL()])


		if first_disjunct != None and second_disjunct != None:
			final_formula = Formula(['|', first_disjunct, second_disjunct])	
		elif first_disjunct == None:
			final_formula = second_disjunct
		elif second_disjunct == None:
			final_formula = first_disjunct

		return final_formula

	def __eq__(self, other):
		if other == None:
			return False
		else:
			return self.label == other.label and self.left == other.left and self.right == other.right


	def prettyPrint(self):
		return self.convert2LTL().prettyPrint()
	

	def __str__(self):
		return self.prettyPrint()		





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
		DT = self.learn_bfs((self.positive_set,self.negative_set), self.formula_dict, upper_bound)

		if DT != None:
			#DT.show()
			return DT, DT.DTSize()
		else:
			return None, upper_bound
	

	def learn_dfs(self, sample_set, cover_dict, upper_bound):

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

		formula1 = self.learn_dfs(split1_set, cover_dict1, upper_bound-best_formula.treeSize()-1)
		formula2 = self.learn_dfs(split2_set, cover_dict2, upper_bound-best_formula.treeSize()-1) # can furthur reduce the size of this tree

		if formula1 == None or formula2 == None:
			return None

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

		if final_formula.treeSize() > upper_bound:
			return None
		else:
			return final_formula
		

	def learn_bfs(self, sample_set, cover_dict, upper_bound):
		
		queue = []

		trueDT = DecisionTree(label=formula_true)
		falseDT = DecisionTree(label=formula_false)
		while True:
			score = 0
			for formula in cover_dict:
				formula_score = (len(cover_dict[formula][0])-len(cover_dict[formula][1])+len(sample_set))/((formula.treeSize())**(0.5)+1)
				if formula_score>score:
					best_formula = formula
					score = formula_score
		
			split1_set = (cover_dict[best_formula][0], cover_dict[best_formula][1])
			split2_set = (sample_set[0].difference(split1_set[0]), sample_set[1].difference(split1_set[1]) )
			
			assert(split1_set[0].union(split2_set[0])==sample_set[0])
			assert(split1_set[1].union(split2_set[1])==sample_set[1])

			if (split1_set[0] == set() and split1_set[1] == set()) or (split2_set[0] == set() and split2_set[1] == set()):
				del(cover_dict[best_formula])
				continue
			else:
				break

		cover_dict1, cover_dict2 = {}, {}
		root_node = DecisionTree(label=best_formula)
		if root_node.DTSize() > upper_bound or cover_dict == {}:
			logging.debug("Size of tree exceeded upper bound")
			return None

		for formula in cover_dict:
			cover_dict1[formula] = (cover_dict[formula][0].difference(split2_set[0]), cover_dict[formula][1].difference(split2_set[1]))
			cover_dict2[formula] = (cover_dict[formula][0].difference(split1_set[0]), cover_dict[formula][1].difference(split1_set[1]))


		queue.append([split1_set, cover_dict1, root_node, 'left'])
		queue.append([split2_set, cover_dict2, root_node, 'right'])

		current_tree_size = root_node.size

		logging.debug('Root node is %s of size %d'%(root_node.label.prettyPrint(), current_tree_size))

		while queue:

			split_set_q, cover_dict_q, parent_node_q, direction = queue.pop()

			if split_set_q[1] == set():
				if direction == 'left':
					parent_node_q.left = trueDT
				if direction == 'right':
					parent_node_q.right = trueDT
				continue
			if split_set_q[0] == set():
				if direction == 'left':
					parent_node_q.left = falseDT
				if direction == 'right':
					parent_node_q.right = falseDT
				continue

			while True:
				score = 0
				for formula in cover_dict_q:
					formula_score = (len(cover_dict_q[formula][0])-len(cover_dict_q[formula][1])+len(split_set_q))/((formula.treeSize())**(0.5)+1)
					if formula_score>score:
						best_formula = formula
						score = formula_score


				split1_set = (cover_dict_q[best_formula][0], cover_dict_q[best_formula][1])
				split2_set = (split_set_q[0].difference(split1_set[0]), split_set_q[1].difference(split1_set[1]))
				

				assert(split1_set[0].union(split2_set[0])==split_set_q[0])
				assert(split1_set[1].union(split2_set[1])==split_set_q[1])

				if (split1_set[0] == set() and split1_set[1] == set()) or (split2_set[0] == set() and split2_set[1] == set()):
					del(cover_dict_q[best_formula])
					continue
				else:
					break


			current_node = DecisionTree(label=best_formula)

			if direction=='left':
				parent_node_q.left = current_node
			if direction=='right':
				parent_node_q.right = current_node

			current_tree_size += current_node.DTSize() + 1

			if current_tree_size >= upper_bound:
				logging.debug("Size of tree exceeded upper bound")
				return None

			if cover_dict == {}:
				logging.debug("Ran out of subtraces for the DT")
				return None

			logging.debug('Current node is %s whose parent is %s and direction is %s. Tree size is %d'%(current_node.label, parent_node_q.label, direction, current_tree_size))

			cover_dict1, cover_dict2 = {}, {}
			for formula in cover_dict_q:
				cover_dict1[formula] = (cover_dict_q[formula][0].difference(split2_set[0]), cover_dict_q[formula][1].difference(split2_set[1]))
				cover_dict2[formula] = (cover_dict_q[formula][0].difference(split1_set[0]), cover_dict_q[formula][1].difference(split1_set[1]))


			queue.insert(0, [split1_set, cover_dict1, current_node, 'left'])
			queue.insert(0, [split2_set, cover_dict2, current_node, 'right'])

		return root_node
				