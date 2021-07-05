from formulaTree import Formula
import random
import sys
	


def lineToTrace(line):
	lasso_start = None
	try:
		traceData, lasso_start = line.split('::')
	except:
		traceData = line
	trace_vector = [tuple([int(varValue) for varValue in varsInTimestep.split(',')]) for varsInTimestep in
				   traceData.split(';')]

	return (trace_vector, lasso_start)


def lineToWord(line):
	lasso_start = None
	try:
		wordData, lasso_start = line.split('::')
	except:
		wordData = line
	wordVector = list(line.split()[0])
	return (wordVector, lasso_start)  


def convertFileType(operators, wordfile, tracefile=None):
	'''
	converts words file type to trace file type
	'''
	sample = Sample(positive=[], negative=[])
	sample.readFromFile(wordfile)
	one_hot_alphabet = {}
	sample.alphabet.sort()
	for i in range(len(sample.alphabet)):
		one_hot_letter = [str(0)]*len(sample.alphabet)
		letter = sample.alphabet[i]
		one_hot_letter[i] = str(1)
		one_hot_alphabet[letter] = one_hot_letter

	if tracefile==None:
		tracefile = wordfile.rstrip('.words')+'.trace'
	with open(tracefile, 'w') as file:
		for word in sample.positive:
			prop_word = ';'.join([','.join(one_hot_alphabet[letter]) for letter in word.vector])
			file.write(prop_word+'\n')

		file.write('---\n')
		for word in sample.negative:
			prop_word = prop_word = ';'.join([','.join(one_hot_alphabet[letter]) for letter in word.vector])
			file.write(prop_word+'\n')
		file.write('---\n')
		file.write(','.join(operators))

class Trace:
	'''
	defines a sequences of letters, which could be a subset of propositions or symbol from an alphabet
	'''
	def __init__(self, vector, is_word, lasso_start=None):
		self.vector = vector
		self.length = len(vector)
		self.is_word = is_word

	def copy(self):
		return self.__init__(self.vector, self.is_word)

	def evaluateFormula(self, formula, letter2pos):
		'''
		evalutates formula on trace
		'''
		nodes = list(set(formula.getAllNodes()))
		self.truthAssignmentTable = {node: [None for _ in range(self.length)] for node in nodes}
		return self.truthValue(formula, 0,letter2pos)

	def truthValue(self, formula, timestep, letter2pos):
		'''
		evaluates formula on trace starting from timestep
		'''
		futureTracePositions = self.futurePos(timestep)
		tableValue = self.truthAssignmentTable[formula][timestep]
		if tableValue != None:
			return tableValue
		else:
			label = formula.label
			if label == 'true':
				val = True
			elif label == 'false':
				val = False
			elif label == '&':
				val = self.truthValue(formula.left, timestep,letter2pos) and self.truthValue(formula.right, timestep,letter2pos)			
			elif label == '|':
				val = self.truthValue(formula.left, timestep, letter2pos) or self.truthValue(formula.right, timestep, letter2pos)			
			elif label == '!':
				val = not self.truthValue(formula.left, timestep, letter2pos)			
			elif label == '->':
				val = not self.truthValue(formula.left, timestep, letter2pos) or self.truthValue(formula.right, timestep, letter2pos)
			elif label == 'F':
				val = max([self.truthValue(formula.left, futureTimestep, letter2pos) for futureTimestep in futureTracePositions])			
			elif label == 'G':
				val = min([self.truthValue(formula.left, futureTimestep, letter2pos) for futureTimestep in futureTracePositions])			
			elif label == 'U':
				val = max(
					[self.truthValue(formula.right, futureTimestep, letter2pos) for futureTimestep in futureTracePositions]) == True \
					   and ( \
								   self.truthValue(formula.right, timestep, letter2pos) \
								   or \
								   (self.truthValue(formula.left, timestep, letter2pos) and self.truthValue(formula,
																								self.nextPos(timestep), letter2pos)) \
						   )
			elif label == 'X':
				try:
					val = self.truthValue(formula.left, self.nextPos(timestep), letter2pos)
				except:
					val = False
			else:	
				if self.is_word:
					val = self.vector[timestep] == label
				else:
					if label == 'L':
						val = (len(self.vector)-1 == timestep)
					else:
						val = self.vector[timestep][letter2pos[label]] # assumes  propositions to be p,q,...
			self.truthAssignmentTable[formula][timestep] = val
			return val

	def __str__(self):
		vector_str = [list(map(lambda x: str(int(x)), letter)) for letter in self.vector]
		return str(';'.join([','.join(letter) for letter in vector_str]))
	
	def __len__(self):
		 return self.length
		

class Sample:
	'''
	contains the sample of postive and negative examples
	'''
	def __init__(self, positive=[], negative=[], alphabet=[], is_words=True):

		self.positive = positive
		self.negative = negative
		self.alphabet = alphabet
		self.is_words = is_words
		self.num_positives = len(self.positive)
		self.num_negatives = len(self.negative)
		self.operators=[]

	
	def extract_alphabet(self, is_word):
		'''
		extracts alphabet from the words/traces provided in the data
		'''
		alphabet = set()
		
		if self.is_words:
			for w in self.positive+self.negative:
				alphabet = alphabet.union(set(w.vector))
			self.alphabet = list(alphabet)
		else:
			self.alphabet = [chr(ord('p')+i) for i in range(len(self.positive[0].vector[0]))] 

	def word2trace(self, word):
		one_hot_alphabet={}
		for i in range(len(self.alphabet)):
			one_hot_letter = [0]*len(self.alphabet)
			letter = self.alphabet[i]
			one_hot_letter[i] = 1
			one_hot_alphabet[letter] = tuple(one_hot_letter)
		trace_list=[]
		for letter in word:
			trace_list.append(one_hot_alphabet[letter])

		return trace_list



	def readFromFile(self, filename):
		'''
		reads .trace/.word files to extract sample from it
		'''
		self.is_words = ('.words' in filename)
		with open(filename, 'r') as file:
			mode = 0
			count=0
			while True:
				count
				line=file.readline()
				if line=='':
					break

				if line == '---\n':
					mode+=1
					continue

				if mode==0:	
					# can read from both word file type and trace file type
					if self.is_words:
						word_vector, lasso_start = lineToWord(line)
						word = Trace(vector=word_vector, lasso_start=lasso_start, is_word=True)	 	
						self.positive.append(word)
					else:
						trace_vector, lasso_start = lineToTrace(line)
						trace = Trace(vector=trace_vector, lasso_start=lasso_start, is_word=False)	 	
						self.positive.append(trace)

				if mode==1:
					
					if self.is_words:
						word_vector, lasso_start = lineToWord(line)
						word = Trace(vector=word_vector, lasso_start=lasso_start, is_word=True)	 	
						self.negative.append(word)
					else:
						trace_vector, lasso_start = lineToTrace(line)
						trace = Trace(vector=trace_vector, lasso_start=lasso_start, is_word=False)	 	
						self.negative.append(trace)

				if mode==2:
					self.operators = list(line.strip().split(','))
				if mode==3:
					self.alphabet = list(line.split(','))


		if mode != 3:		
				self.extract_alphabet(self.is_words)
		

		self.alphabet.sort()
		self.letter2pos={}
		for i in range(len(self.alphabet)):
			self.letter2pos[self.alphabet[i]]=i
		
		if self.is_words:
			for word in self.positive+ self.negative:
				word.vector= self.word2trace(word.vector)
				word.vector_str= str(word.vector)
				word.is_word = False

	def isFormulaConsistent(self, formula):
		'''
		checks if the sample is consistent with given formula
		'''
		if formula == None:
			return True
		for w in self.positive:
			if w.evaluateFormula(formula,self.letter2pos) == False:
				print('positive', str(w))
				return False

		for w in self.negative:
			if w.evaluateFormula(formula,self.letter2pos) == True:
				print('negative', str(w))
				return False
		return True

	def random_trace(self, 
		alphabet = ['p','q','r'], 
		length = 5,
		is_words = True):

		if is_words:
			rand_word = ''
			for j in range(length_word):
				rand_letter = random.choice(alphabet)
				rand_word += rand_letter
			return Trace(rand_word, is_word=True)
		else:
			trace_vector = [ [random.randint(0,1) for _ in range(len(alphabet))] for _ in range(length_trace) ]
			return Trace(trace_vector, is_word=False)

	def generator(self, 
		formula=None, 
		filename='generated.words', 
		num_traces=(5,5), 
		length_traces=None, 
		alphabet = ['p','q','r'], 
		length_range=(5,15), 
		is_words=True, 
		operators=['G', 'F', '!', 'U', '&','|', '->', 'X']):

		num_positives = 0
		total_num_positives = num_traces[0]
		num_negatives = 0
		total_num_negatives = num_traces[1]
		ver = True
		letter2pos = {alphabet[i]:i for i in range(len(alphabet))}

		while num_positives < total_num_positives or num_negatives < total_num_negatives:

			length = random.randint(length_range[0], length_range[1])
			final_trace = self.random_trace(alphabet, length, is_words)

			#check
			if formula != None:
				ver = final_trace.evaluateFormula(formula, letter2pos)

			if num_positives < total_num_positives:
				if ver == True or formula == None:
					self.positive.append(final_trace)
					num_positives += 1
					continue

			if num_negatives < total_num_negatives:
				if ver == False or formula == None:
					self.negative.append(final_trace) 
					num_negatives += 1

			# sys.stdout.write("\rGenerating sample: created %d positives, %d negatives "%(num_positives, num_negatives))
			# sys.stdout.flush()

		self.operators = operators
		self.writeToFile(filename)

	def random_edit(self,
		trace,
		alphabet = ['p','q','r'], 
		is_words = True):

		length = trace.length
		rand_position = random.randrange(length)
		if is_words:
			rand_letter = random.choice(alphabet)
		else:
			rand_letter = [random.randint(0,1) for _ in range(len(alphabet))]
		trace[rand_position] = rand_letter

	def generator_random_walk(self, 
		formula=None, 
		filename='generated.words', 
		num_traces=(5,5), 
		length_traces=None, 
		alphabet = ['p','q','r'], 
		length_range=(5,15), 
		is_words=True, 
		operators=['G', 'F', '!', 'U', '&','|', '->', 'X']):

		total_num_positives = num_traces[0]
		total_num_negatives = num_traces[1]
		assert(total_num_positives == total_num_negatives)
		assert(formula != None)

		letter2pos = {alphabet[i]:i for i in range(len(alphabet))}

		for i in range(total_num_positives):
			length = random.randint(length_range[0], length_range[1])
			
			first_trace = self.random_trace(alphabet, length, is_words)
			first_ver = first_trace.evaluateFormula(formula, letter2pos)

			second_trace = self.copy(first_trace)
			second_ver = second_trace.evaluateFormula(formula, letter2pos)

			i = 0
			while first_ver == second_ver and i < 1e6:
				second_trace = self.random_edit(second_trace, alphabet, length, is_words)
				second_ver = second_trace.evaluateFormula(formula, letter2pos)
				i += 1
			assert(first_ver != second_ver)

			if first_ver:
				self.positive.append(first_trace)
				self.negative.append(second_trace)
			else:
				self.negative.append(first_trace)
				self.positive.append(second_trace)

		self.operators = operators
		self.writeToFile(filename)

	def writeToFile(self, filename):

		with open(filename, 'w') as file:
			for trace in self.positive:

				file.write(str(trace)+'\n')
			file.write('---\n')

			for trace in self.negative:
				file.write(str(trace)+'\n')


			if self.operators!=[]:
				file.write('---\n')
				file.write(','.join(self.operators)+'\n')

			if self.alphabet != []:
				file.write('---\n')
				file.write(','.join(self.alphabet))
