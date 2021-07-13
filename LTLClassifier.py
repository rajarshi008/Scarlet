from inferLTL import inferLTL
from sample import Sample, Trace
import logging
import time


logging.basicConfig(format='%(message)s', level=logging.DEBUG)

def word2trace(word, alphabet):
	'''
	Converts word object to trace object
	'''
	one_hot_alphabet={}
	for i in range(len(alphabet)):
		one_hot_letter = [0]*len(alphabet)
		letter = alphabet[i]
		one_hot_letter[i] = 1
		one_hot_alphabet[letter] = tuple(one_hot_letter)
	trace_list=[]
	for letter in word:
		trace_list.append(one_hot_alphabet[letter])

	return trace_list


def preProcessSample(sample_file):
	'''
	reads a multi-class sample data and returns a list of samples (one for each class) and the class labels
	'''
	trace_list = []
	label_list = []
	with open(sample_file, 'r') as file:
		alphabet = set()
		trace_count = 0
		while True:
			line = file.readline()
			if line == '':
				break
			else:
				trace_count+=1
				word_str, class_label = line.split(';')
				
				word_vector = word_str.split(',')
				word = Trace(vector=word_vector, is_word=True)
				trace_list.append(word)
				
				label_list.append(int(class_label))
				
				alphabet = alphabet.union(set(word_vector))
				

	alphabet = list(alphabet)
	print(alphabet)
	logging.debug('Read %d traces with %d size alphabet and %d classes'%(len(trace_list),len(alphabet), len(set(label_list))))
	
	for word in trace_list:
		word.vector = word2trace(word.vector, alphabet)
		word.vector_str = str(word.vector)
		word.is_word = False

	

	return trace_list, label_list, alphabet





# def LTL_list(sample_file):
# 	'''
# 	reads a multi-class data and returns list of LTL formulas (one for each class)
# 	'''
# 	label2samples, class_list = multipleSamples(sample_file)
# 	label2LTLs = {}
# 	for i in class_list:
# 		logging.debug('Generating LTL formula for class label %d'%i)
# 		time1 = time.time() 
# 		label2LTLs[i] = inferLTL(label2samples[i])
# 		time1 = time.time() - time1
# 		logging.debug('Took time %.3f'%time1)

# 	print(label2LTLs)

def main():
	
	#Input preprocessing
	sample_file = 'traces/alfred/full.txt' 
	X_train, y_train, alphabet = preProcessSample(sample_file)

	#Calculate LTL formulas
	lc = LTLclassfier()
	lc.fit(X_train, y_train, alphabet)

	#Calculate prediction score
	#X_train, _, alphabet = preProcessSample(sample_file)	
	#lc.predict(X_values, letter2pos)



class LTLclassfier():

	def __init__(self):
		self.LTL_list = []

	def fit(self, X_train, y_train, alphabet):
		
		classes = set(y_train)
		label2samples = {label:Sample(positive=[], negative=[], is_words=True) for label in classes}
		letter2pos = {alphabet[i]:i for i in range(len(alphabet))}
		
		for i in label2samples:
			label2samples[i].alphabet = alphabet
			label2samples[i].letter2pos = letter2pos
		
		for i in range(len(X_train)):
			label2samples[y_train[i]].positive.append(X_train[i])
			for label in classes:
				if label != y_train[i]:
					label2samples[label].negative.append(X_train[i])
			
		for label in classes:
			logging.debug('Generating LTL formula for class label %d'%label)
			time1 = time.time()
			self.LTL_list.append(inferLTL(label2samples[label]))
			time1 = time.time() - time1
			logging.debug('Took time %.3f'%time1)



	def predict(X_values, letter2pos):
		pass
		

		

main()
#LTL_list('traces/alfred/full.txt')







