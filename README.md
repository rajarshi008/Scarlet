<h1 align="center">
  <img src="https://rajarshi008.github.io/assets/images/scarlet-logo.png" width="60%">
 </h1>

---

## SCARLET 

We solve the problem of learning LTL formulas from a sample consisting of traces partitioned into positive and negative.

A [paper](https://link.springer.com/chapter/10.1007/978-3-030-99524-9_14) presenting the algorithms behind `Scarlet` was published in TACAS'2022.

## Input File format:

The input files consist of traces separated as positives and negatives, separated by `---`.
Each trace is a sequence of letter separated by `;`. Each letter represents the truth value of atomic propositions.
An example of a trace is `1,0,1;0,0,0` which consists of two letters each of which define the values of three propositions (which by default consider to be `p,q,r`). An example input file looks like the following:
```
0,0,0;0,1,1;1,0,0;0,0,1;0,1,0
1,1,0;1,0,1;1,0,0;1,1,1;1,0,1
1,1,0;0,1,1;1,1,1;1,0,0;1,0,1
---
1,0,0;1,0,0;0,1,0;1,1,0;1,1,1
1,0,0;1,0,0;0,1,0;1,1,0;1,0,0
0,0,1;1,0,0;1,1,0;1,1,1;1,0,0
```
For `Scarlet` to work, you must save your input files with the extension  `.trace`.


There are two ways of using `Scarlet` depending on what one prefers. One can use `Scarlet` using its python API  or using its command-line features. Here, we provide the instructions to use both.
## Python API

### Installation

Now, you can install the tool, as python package using pip command as follows:

```
python3 -m pip install Scarlet-ltl
```

### Basic API Usage
We now provide the basic usage of the Scarlet python API.
```
from Scarlet.ltllearner import LTLlearner
learner = LTLlearner(input_file = input_file_name)
learner.learn()
```
Note that the python API does not provide any example input files.
Hence, you must create your trace file in a format as described above and provide it to the API.

### Parameters
You can call the `LTLlearner` class with additional parameters as follows:

* input_file = the path of the file containing LTL formuas, e.g., `= 'example.trace'`
* timeout = For specifying the timeout, `default = 900`
* csvname = the name of the output csv file, e.g.,  `= 'result.csv'`
* thres = the bound on loss function for noisy data, `default = 0` for perfect classification, has to be a number between zero and one


### Generation of (random) Trace Files from LTL formulas

You can also generate trace files from given LTL formulas following the instructions below:

#### Installation of Dependencies

For generating benchmarks from a given set of LTL formula, we rely on a python package LTLf2DFA that uses [MONA](https://www.brics.dk/mona/) in its backend. 
As a result, one needs to install MONA first in order to be able to use this procedure (instructions can be found in the MONA website).

#### Creating Input Formula File

For generating benchmarks, you have to create an input file named `formulas.txt` in the same directory where `venv` folder is located. The formula file should contain a list of formulas (in prefix notation) along with the alphabet.
An example of this file is as follows:

```
G(!(p));p
|(G(!(p)),F(&(p, F(q))));p,q
G(->(q, G(!(p))));p,q
```

#### Generating Trace Files for a given Formula File

```
from Scarlet.genBenchmarks import SampleGenerator
generator = SampleGenerator(formula_file= "formulas.txt")
generator.generate()
```

#### Parameters
You can call the `SampleGenerator` class with additional parameters as follows:

* formula_file = the path of the file containing LTL formuas, `example = 'formulas.txt'`
* sample_sizes = list of sample_size, i.e., number of positive traces and number of negative traces (separated by comma) in each sample, `default = [(10,10),(50,50)]`
* trace_lengths = For specifying the length range for each trace in the samples, `default = [(6,6)]`
* output_folder = For specifying the name of the folder in which samples are generated

The PyPi package for this API can be found in [this link](https://pypi.org/project/Scarlet-ltl/0.0.2/).


## Command Line Usage

### Installation
To build from source, use the following set of commands: 
```
git clone https://github.com/rajarshi008/Scarlet.git
cd Scarlet
source ./installation.sh
```

### Running


Run using `python -m Scarlet.ltllearner`. By default, this will run *Scarlet* on `example.trace` located inside the Scarlet folder. For easy testing, one can replace `example.trace` with the trace file of choice (see `All_benchmarks` for more example traces). Further, there are a variety of arguments that one can use to run *Scarlet*, as listed below:

|Argument        |Meaning
|----------------|------------------------------
|-i <file_name>| For specifying the name of the input file (to be located inside the `Scarlet` folder), default is *example.trace*.
|-v | For outputting a detailed log of *Scarlet*'s execution.
|-vv | For outputting a even more detailed log of *Scarlet*'s execution.
|-t <timeout>| For specifying the timeout, default is 900 secs (the best formula found till timeout can be found in result.csv, located in the `Scarlet` folder).
|-o <result_file_name>| For specifying the name of the output csv file, default is *results.csv*
|-l <noise_threshold>| For specifying the bound on loss function for noisy data, default is *0* for perfect classification.	
|-h | For outputting the help.


### Generation of (random) Trace Files from LTL formulas

For generating benchmarks from a given set of LTL formula, we rely on a python package LTLf2DFA that uses [MONA](https://www.brics.dk/mona/) in its backend. 
As a result, one needs to install MONA first in order to be able to use this procedure (instructions can be found in the MONA website).

After the installation, for generating samples one simply needs to run `python -m Scarlet.genBenchmarks`. By default, this generates samples that are separable using the formulas provided in `formulas.txt`. You can run the command with the following arguments:

|Argument        |Meaning
|----------------|------------------------------
|-f<file_name>| For specifying the file containing all of the formulas (in prefix notation).
|-s <list_of_tuple>| List of sample_size, i.e., number of positive traces and number of negative traces (separated by comma) in each sample.  
|-l <list_of_tuple>| For specifying the length range for each trace in the samples 
|-o <output_folder>| For specifying the name of the folder in which samples are generated.
|-h | Outputs the help.

The formula file should contain a list of formulas (in prefix notation) along with the alphabet (see `formulas.txt`) and should be located inside the `Scarlet` folder to be used for generating the sample.