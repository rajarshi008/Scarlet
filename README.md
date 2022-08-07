## SCARLET 
---

![](scarlet-logo.png)

We solve the problem of learning LTL formulas from a sample consisting of traces partitioned into positive and negative.
A [paper](https://link.springer.com/chapter/10.1007/978-3-030-99524-9_14) presenting the algorithms behind `Scarlet` was published in TACAS'2022.

## Installation

You can install the tool, as python package using pip command as follows:

```
pip install
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

## How to run:

### Run Scarlet on a particular input file

* Create the input file

Create an input file with `.trace` extension. The file format should follow the proper format from the above sub-section.

* Run the LTL learner
```
from Scarlet.run_tests import LTLlearner
learner = LTLlearner()
learner.learn()
```
This will run Scarlet on the input trace file.

### For generating samples from LTL formulas

For generating benchmarks from a given set of LTL formula, we rely on a python package LTLf2DFA that uses [MONA](https://www.brics.dk/mona/) in its backend. 
As a result, one needs to install MONA first in order to be able to use this procedure (instructions can be found in the MONA website).

* Input the LTL formulas



After the installation, for generating samples one simply needs to run `python genBenchmarks.py`. By default, this generates samples that are separable using the formulas provided in `formulas.txt`. You can run `genBenchmarks.py` with the following arguments:

|Argument        |Meaning
|----------------|------------------------------
|--formula_file <file_name>| For specifying the file containing all of the formulas (in prefix notation).
|--size <list_of_tuple>| List of sample_size, i.e., number of positive traces and number of negative traces (separated by comma) in each sample.  
|--lengths <list_of_tuple>| For specifying the length range for each trace in the samples 
|--trace_type <type_of_sample> | For specifying whether you want to generate trace type files or word type files.
|-o <output_folder>| For specifying the name of the folder in which samples are generated.
|-h | Outputs the help.

The formula file should contain a list of formulas (in prefix notation) along with the alphabet (see `formulas.txt`) to be used for generating the sample.