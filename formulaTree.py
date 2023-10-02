import pdb
import re 
from lark import Lark, Transformer
from graphviz import Source


unary_operators = ['G', 'F', '!', 'X']
binary_operators = ['&', '|', 'U', '->']

class SimpleTree:
	def __init__(self, label = "dummy"):	
		self.left = None
		self.right = None
		self.label = label
	
	def __hash__(self):
		# return hash((self.label, self.left, self.right))
		return hash(self.label) + id(self.left) + id(self.right)
	
	def __eq__(self, other):
		if other is None:
			return False
		else:
			return self.label == other.label and self.left == other.left and self.right == other.right
	
	def __ne__(self, other):
		return not self == other
	
	def _isLeaf(self):
		return self.right is None and self.left is None
	
	def _addLeftChild(self, child):
		if child is None:
			return
		if type(child) is str:
			child = SimpleTree(child)
		self.left = child
		
	def _addRightChild(self, child):
		if type(child) is str:
			child = SimpleTree(child)
		self.right = child
	
	def addChildren(self, leftChild = None, rightChild = None): 
		self._addLeftChild(leftChild)
		self._addRightChild(rightChild)
		
		
	def addChild(self, child):
		self._addLeftChild(child)
		
	def getAllNodes(self):
		leftNodes = []
		rightNodes = []
		
		if not self.left is None:
			leftNodes = self.left.getAllNodes()
		if not self.right is None:
			rightNodes = self.right.getAllNodes()
		return [self] + leftNodes + rightNodes

	def getAllLabels(self):
		if not self.left is None:
			leftLabels = self.left.getAllLabels()
		else:
			leftLabels = []
			
		if not self.right is None:
			rightLabels = self.right.getAllLabels()
		else:
			rightLabels = []
		return [self.label] + leftLabels + rightLabels

	def __repr__(self):
		if self.left is None and self.right is None:
			return self.label
		
		# the (not enforced assumption) is that if a node has only one child, that is the left one
		elif (not self.left is None) and self.right is None:
			return self.label + '(' + self.left.__repr__() + ')'
		
		elif (not self.left is None) and (not self.right is None):
			return self.label + '(' + self.left.__repr__() + ',' + self.right.__repr__() + ')'

'''
A class for encoding syntax Trees and syntax DAGs of LTL formulas
'''

class Formula(SimpleTree):
	
	def __init__(self, formulaArg = "dummyF"):
		self.size = None
		if not isinstance(formulaArg, str):
			self.label = formulaArg[0]
			self.left = formulaArg[1]
			try:
				self.right = formulaArg[2]
			except:
				self.right = None

		else:
			super().__init__(formulaArg)

		# self.eval = [word][pos] = True / False

	def __lt__(self, other):

		if self.getDepth() < other.getDepth():
			return True
		elif self.getDepth() > other.getDepth():
			return False
		else:
			if self._isLeaf() and other._isLeaf():
				return self.label < other.label

			if self.left != other.left:
				return self.left < other.left

			if self.right is None:
				return False
			if other.right is None:
				return True
			if self.right != other.right:
				return self.right < other.right

			else:
				return self.label < other.label


	def prettyPrint(self, top=False):
		if top is True:
			lb = ""
			rb = ""
		else:
			lb = "("
			rb = ")"
		if self._isLeaf():
			return self.label
		if self.label in unary_operators:
			return lb + self.label +" "+ self.left.prettyPrint() + rb
		if self.label in binary_operators:
			return lb + self.left.prettyPrint() +" "+  self.label +" "+ self.right.prettyPrint() + rb

	
	def getAllVariables(self):
		allNodes = list(set(self.getAllNodes()))
		return [ node for node in allNodes if node._isLeaf() == True ]
	
	def getDepth(self):
		if self.left is None and self.right is None:
			return 0
		leftValue = -1
		rightValue = -1
		if not self.left is None:
			leftValue = self.left.getDepth()
		if not self.right is None:
			rightValue = self.right.getDepth()
		return 1 + max(leftValue, rightValue)
	
	def getNumberOfSubformulas(self):
		return len(self.getSetOfSubformulas())
	
	def getSetOfSubformulas(self):
		if self.left is None and self.right is None:
			return [repr(self)]
		leftValue = []
		rightValue = []
		if not self.left is None:
			leftValue = self.left.getSetOfSubformulas()
		if not self.right is None:
			rightValue = self.right.getSetOfSubformulas()
		return list(set([repr(self)] + leftValue + rightValue))

	
	def treeSize(self):
		if self.size is None:
			if self.left is None and self.right is None:
				if self.label == 'true' or self.label == 'false':
					self.size = 0
				else:
					self.size = 1
			leftSize=0
			rightSize=0
			if not self.left is None:
				leftSize= self.left.treeSize()
			if not self.right is None:
				rightSize = self.right.treeSize()
			self.size = 1+ leftSize + rightSize

		return self.size


	@classmethod
	def convertTextToFormula(cls, formulaText):
	    
	    f = Formula()
	    try:
	        formula_parser = Lark(r"""
	            ?formula: _binary_expression
	                    |_unary_expression
	                    | constant
	                    | variable
	            !constant: "true"
	                    | "false"
	            _binary_expression: binary_operator "(" formula "," formula ")"
	            _unary_expression: unary_operator "(" formula ")"
	            variable: /[a-z]/
	            !binary_operator: "&" | "|" | "->" | "U"
	            !unary_operator: "F" | "G" | "!" | "X"
	            
	            %import common.SIGNED_NUMBER
	            %import common.WS
	            %ignore WS 
	         """, start = 'formula')
	    
	        
	        tree = formula_parser.parse(formulaText)
	        
	    except Exception as e:
	        print("can't parse formula %s" %formulaText)
	        print("error: %s" %e)
	        
	    
	    f = TreeToFormula().transform(tree)
	    return f
			
class TreeToFormula(Transformer):
        def formula(self, formulaArgs):
            
            return Formula(formulaArgs)
        def variable(self, varName):
            return Formula([str(varName[0]), None, None])
        def constant(self, arg):
            connector = ""
            if str(arg[0]) == "true":
                connector = "|"
            elif str(arg[0]) == "false":
                connector = "&"
            return Formula([connector, Formula(["p", None, None]), Formula(["!", Formula(["p", None, None] ), None])])
                
        def binary_operator(self, args):
            return str(args[0])
        def unary_operator(self, args):
            return str(args[0])



def merge(operator, formula1, formula2):
	"""
	merges common operators from 2 formulas
	"""
	if formula1.label == formula2.label:
		if operator == "&":
				if formula1.label == 'X' or formula1.label == 'G':
					return Formula([formula1.label, merge('&', formula1.left, formula2.left)])
				if formula1.label == '!':
					return Formula([formula1.label, merge('|', formula1.left, formula2.left)])
				if formula1.label == '&' or formula1.label == '|':
					if formula1.left == formula2.left:
						return Formula([formula1.label, formula1.left, merge('&',formula1.right, formula2.right)])
					elif formula1.left == formula2.right:
						return Formula([formula1.label, formula1.left, merge('&',formula1.right, formula2.left)])
					elif formula1.right == formula2.left:
						return Formula([formula1.label, formula1.right, merge('&',formula1.left, formula2.right)])
					elif formula1.right == formula2.right:
						return Formula([formula1.label, formula1.right, merge('&',formula1.left, formula2.left)])



		elif operator == "|":			
				if formula1.label == 'X' or formula1.label == 'F':
					return Formula([formula1.label, merge('|', formula1.left, formula2.left)])
				if formula1.label == '!':
					return Formula([formula1.label, merge('&', formula1.left, formula2.left)])
				if formula1.label == '&' or formula1.label == '|':
					if formula1.left == formula2.left:
						return Formula([formula1.label, formula1.left, merge('|',formula1.right, formula2.right)])
					elif formula1.left == formula2.right:
						return Formula([formula1.label, formula1.left, merge('|',formula1.right, formula2.left)])
					elif formula1.right == formula2.left:
						return Formula([formula1.label, formula1.right, merge('|',formula1.left, formula2.right)])
					elif formula1.right == formula2.right:
						return Formula([formula1.label, formula1.right, merge('|',formula1.left, formula2.left)])

		
	return Formula([operator, formula1, formula2])
	




def display(formula):
	'''
	displays the formula in jpg format
	'''
	formula_queue = []
	formula_id = {formula: 1}
	edges = []

	if not formula.left is None:
		formula_queue.append(formula.left)
		formula_id[formula.left] = 2*formula_id[formula]
		edges.append((formula_id[formula],formula_id[formula.left]))
	if not formula.right is None:
		formula_queue.append(formula.right)
		formula_id[formula.right] = 2*formula_id[formula]+1
		edges.append((formula_id[formula],formula_id[formula.right]))

	while not formula_queue is []:
		curr_formula = formula_queue.pop()
		print(curr_formula)
		if not curr_formula.left is None:
			formula_queue.append(curr_formula.left)
			formula_id[curr_formula.left] = 2*formula_id[curr_formula]
			edges.append((formula_id[curr_formula],formula_id[curr_formula.left]))
		if not curr_formula.right is None:
			formula_queue.append(curr_formula.right)
			formula_id[curr_formula.right] = 2*formula_id[curr_formula]+1
			edges.append((formula_id[curr_formula],formula_id[curr_formula.right]))


	dot_str =  "digraph g {\n"


	for formula in formula_id:
		dot_str += ('{} [label="{}"]\n'.format(formula_id[formula], formula.label))
	for edge in edges:
		dot_str += ('{} -> {}\n'.format(edge[0],edge[1]))


	dot_str += ("}\n")
	s = Source(dot_str, filename="test.gv", format="png")
	s.view()
	

formula_true = Formula('true')
formula_false = Formula('false')
formula_true.size = 0
formula_false.size = 0


#formula = Formula.convertTextToFormula("G(X(&(p,q)))")