<h1 align="center">
  <img src="https://rajarshi008.github.io/assets/images/scarlet-logo.png" width="60%">
 </h1>
<p  align="center">
<a href="https://zenodo.org/doi/10.5281/zenodo.10357544"><img src="https://zenodo.org/badge/365867297.svg" alt="DOI"></a>
</p>
We consider the problem of learning explainable models in Linear Temporal Logic (LTL) using system executions partitioned into positive (or desirable) and negative (or undesirable).

Our paper "[Scalable Anytime Algorithms for Learning Fragments of Linear Temporal Logic](https://link.springer.com/chapter/10.1007/978-3-030-99524-9_14)" presenting the algorithms behind *Scarlet* was published in TACAS'2022.

**Table of Contents**
<!-- toc -->

- [Input File format](#input-file-format)
- [Python API](#python-api)
  - [API Installation](#api-installation)
  - [Basic API Usage](#basic-api-usage)
    - [API Parameters](#api-parameters)
  - [Generation of Trace Files using API](#generation-of-trace-files-using-api)
    - [Installation of Dependencies](#installation-of-dependencies)
    - [Generating from a given Formula File](#generating-from-a-given-formula-file)
    - [API Generation Parameters](#api-generation-parameters)
- [Command Line Usage](#command-line-usage)
  - [CMD Installation](#cmd-installation)
  - [CMD Running](#cmd-running)
    - [CMD Parameters](#cmd-parameters)
  - [Generation of Trace Files using CMD](#generation-of-trace-files-using-cmd)
    - [CMD Generation Parameters](#cmd-generation-parameters)
  - [Testing](#testing)
- [Report an issue](#report-an-issue)
- [Contribute](#contribute)

<!-- tocstop -->


## Input File format:

The input files consist of system executions, formally termed as traces, separated as positives and negatives, separated by `---`.
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
For *Scarlet* to work, you must save your input files with the extension  `.trace`.


There are two ways of using *Scarlet*: using its python API or using its command-line features. Here, we provide the instructions to use both.
## Python API

### Python Installation

Now, you can install the tool, as python package using pip command as follows:

```
python3 -m pip install Scarlet-ltl
```

### Basic API Usage
We now provide the basic usage of the *Scarlet* python API.
```
from Scarlet.ltllearner import LTLlearner
learner = LTLlearner(input_file = input_file_path)
learner.learn()
```
Note that the python API does not provide any example input files.
Hence, you must create your trace file in a format as described in the previous section and provide it to the API.

#### API Parameters
You can call the `LTLlearner` class with additional parameters as follows:

* input_file = the path of the file containing LTL formuas, e.g., `= 'example.trace'`
* timeout = For specifying the timeout, `default = 900`
* csvname = the name of the output csv file, e.g.,  `= 'result.csv'`
* thres = the bound on loss function for noisy data, `default = 0` for perfect classification, has to be a number between zero and one


### Generation of Trace Files using API

You can also generate trace files from given LTL formulas following the instructions below:

#### Installation of Dependencies

For generating benchmarks from a given set of LTL formula, we rely on a python package LTLf2DFA that uses [*MONA*](https://www.brics.dk/mona/) in its backend. 
As a result, one needs to install *MONA* first in order to be able to use this procedure (instructions can be found in the *MONA* website).

#### Creating Input Formula File

For generating benchmarks, you have to create an input file named `formulas.txt` in the same directory where `venv` folder is located. The formula file should contain a list of formulas (in prefix notation) along with the alphabet.
An example of this file is as follows:

```
G(!(p));p
|(G(!(p)),F(&(p, F(q))));p,q
G(->(q, G(!(p))));p,q
```

#### Generating from a given Formula File

```
from Scarlet.genBenchmarks import SampleGenerator
generator = SampleGenerator(formula_file= "formulas.txt")
generator.generate()
```

#### API Generation Parameters 
You can call the `SampleGenerator` class with additional parameters as follows:

* formula_file = the path of the file containing LTL formuas, `example = 'formulas.txt'`
* sample_sizes = list of sample_size, i.e., number of positive traces and number of negative traces (separated by comma) in each sample, `default = [(10,10),(50,50)]`
* trace_lengths = For specifying the length range for each trace in the samples, `default = [(6,6)]`
* output_folder = For specifying the name of the folder in which samples are generated

The PyPi package for this API can be found in [this link](https://pypi.org/project/Scarlet-ltl/0.0.2/).


## Command Line Usage

### CMD Installation
To build from source, use the following set of commands: 
```
git clone https://github.com/rajarshi008/Scarlet.git
cd Scarlet
source ./installation.sh
```

### CMD Running

Run using `python -m Scarlet.ltllearner`. By default, this will run `Scarlet` on `example.trace` located inside the `Scarlet` folder. For easy testing, one can replace `example.trace` with the trace file of choice (see `All_benchmarks` for more example traces). 

#### CMD Parameters
There are a variety of arguments that one can use to run *Scarlet*, as listed below:

|Argument        |Meaning
|----------------|------------------------------
|-i <file_path>| For specifying the name of the input file (to be located inside the `Scarlet` folder), default is *example.trace*.
|-v | For outputting a detailed log of `Scarlet`'s execution.
|-vv | For outputting a even more detailed log of `Scarlet`'s execution.
|-t <timeout>| For specifying the timeout, default is 900 secs (the best formula found till timeout can be found in result.csv, located in the `Scarlet` folder).
|-o <result_file_name>| For specifying the name of the output csv file, default is *results.csv*
|-l <noise_threshold>| For specifying the bound on loss function for noisy data, default is *0* for perfect classification.	
|-h | For outputting the help.


### Generation of Trace Files using CMD

For generating benchmarks from a given set of LTL formula, we rely on a python package LTLf2DFA that uses [*MONA*](https://www.brics.dk/mona/) in its backend. 
As a result, one needs to install *MONA* first in order to be able to use this procedure (instructions can be found in the *MONA* website).

After the installation, for generating samples one simply needs to run `python -m Scarlet.genBenchmarks`. By default, this generates samples that are separable using the formulas provided in `formulas.txt`. 

#### CMD Generation Parameters
You can run the command with the following arguments:

|Argument        |Meaning
|----------------|------------------------------
|-f<file_name>| For specifying the file containing all of the formulas (in prefix notation).
|-s <list_of_tuple>| List of sample_size, i.e., number of positive traces and number of negative traces (separated by comma) in each sample.  
|-l <list_of_tuple>| For specifying the length range for each trace in the samples 
|-o <output_folder>| For specifying the name of the folder in which samples are generated.
|-h | Outputs the help.

The formula file should contain a list of formulas (in prefix notation) along with the alphabet (see `formulas.txt`) and should be located inside the `Scarlet` folder to be used for generating the sample.

### Testing
For testing all features of the tool use: `python -m pytest Scarlet` (Installation of *MONA* is required).
For testing only the features of LTL learning use: `python -m pytest Scarlet/tests/test_learner`.
For testing only the features of trace file generation use: `python -m pytest Scarlet/tests/test_generator` (Installation of *MONA* is required).


## Report an issue

If you find any issue, please create a GitHub issue with specifics steps to reproduce the bug.

## Contribute

Contributions are welcome! Please first, create an issue with what your contribution should be about.
Then you can create a pull request.
