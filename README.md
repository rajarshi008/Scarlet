<h1 align="center">
  <img src="https://rajarshi008.github.io/assets/images/scarlet-logo.png" width="60%">
 </h1>


---
## SCARLET 


We solve the problem of learning LTL formulas from a sample consisting of traces partitioned into positive and negative.
A [paper](https://link.springer.com/chapter/10.1007/978-3-030-99524-9_14) presenting the algorithms behind `Scarlet` was published in TACAS'2022.

## Installation

### Installing the tool

Now, you can install the tool, as python package using pip command as follows:

```
python3 -m pip install Scarlet-ltl
```

### Input File format:

The input files consist of traces separated as positives and negatives, separated by `---`.
Each trace is a sequence of letter separated by `;`. Each letter represents the truth value of atomic propositions.
An example of a trace is `1,0,1;0,0,0` which consists of two letters each of which define the values of three propositions (which by default consider to be `p,q,r`). An example sample looks like the following:
```
0,0,0;0,1,1;1,0,0;0,0,1;0,1,0
1,1,0;1,0,1;1,0,0;1,1,1;1,0,1
1,1,0;0,1,1;1,1,1;1,0,0;1,0,1
---
1,0,0;1,0,0;0,1,0;1,1,0;1,1,1
1,0,0;1,0,0;0,1,0;1,1,0;1,0,0
0,0,1;1,0,0;1,1,0;1,1,1;1,0,0
```

## How to run Scarlet:

### Create input file

To run Scarlet, you have to create an input file with `.trace` extension in the same directory where `venv` folder is located. The input file format is described in the above section.

### Run Scarlet on a particular input file

```
from Scarlet.ltllearner import LTLlearner
learner = LTLlearner(input_file = "input_file_name.trace")
learner.learn()
```
This will run Scarlet on the input trace file.

### Parameters
You can call the `LTLlearner` class with additional parameters as follows:

* input_file = the path of the file containing LTL formuas, i.e., `= 'input_file_name.trace'`
* timeout = For specifying the timeout, `default = 900`
* csvname = the name of the output csv file, i.e.,  `= 'output_file_name.csv'`
* thres = the bound on loss function for noisy data, `default = 0` for perfect classification, has to be a number between zero and one


## How to generate trace files from LTL formulas

You can also generate trace files from given LTL formulas following the instructions below:

### Install dependencies

For generating benchmarks from a given set of LTL formula, we rely on a python package LTLf2DFA that uses [MONA](https://www.brics.dk/mona/) in its backend. 
As a result, one needs to install MONA first in order to be able to use this procedure (instructions can be found in the MONA website).

### Create input formula file

For generating benchmarks, you have to create an input file named `formulas.txt` in the same directory where `venv` folder is located. The formula file should contain a list of formulas (in prefix notation) along with the alphabet.
An example of this file is as follows:

```
G(!(p));p
->(F(q), U(!(p),q));p,q
G(->(q, G(!(p))));p,q
```

### Generate trace files from `formulas.txt`

```
from Scarlet.genBenchmarks import SampleGenerator
generator = SampleGenerator(formula_file= "formulas.txt")
generator.generate()
```

### Parameters
You can call the `SampleGenerator` class with additional parameters as follows:

* formula_file = the path of the file containing LTL formuas, `example = 'formulas.txt'`
* sample_sizes = list of sample_size, i.e., number of positive traces and number of negative traces (separated by comma) in each sample, `default = [(10,10),(50,50)]`
* trace_lengths = For specifying the length range for each trace in the samples, `default = [(6,6)]`
* output_folder = For specifying the name of the folder in which samples are generated


