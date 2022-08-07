## SCARLET 
---

![](scarlet-logo.png)

We solve the problem of learning LTL formulas from a sample consisting of traces partitioned into positive and negative.
A [paper](https://link.springer.com/chapter/10.1007/978-3-030-99524-9_14) presenting the algorithms behind `Scarlet` was published in TACAS'2022.

## Installation


To build from source, use the following set of commands:
```
git clone https://github.com/rajarshi008/Scarlet.git
cd Scarlet
source ./installation.sh
```
You can also install as python package using pip command. To do so, follow *this*.

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

### For running the LTL learner

Run using `python -m Scarlet.run_tests`. By default, this will run *Scarlet* on `example.trace`. For easy testing, one can replace `example.trace` with the trace file of choice. Further, there are a variety of arguments that one can use to run *Scarlet*, as listed below:

|Argument        |Meaning
|----------------|------------------------------
|-i <file_name>| For specifying the path of the input file, default is *example.trace*.
|-v | For output a detailed log of *Scarlet*'s execution.
|-vv | For output a even more detailed log of *Scarlet*'s execution.
|-t <timeout>| For specifying the timeout, default is 900 secs (the best formula found till timeout can be found in result.csv).
|-o <result_file_name>| For specifying the name of the output csv file, default is *results.csv*
|-m <bool_comb_method>| For specifying the method (SC for set cover, DT for Decision Tree) for boolean combination, default is *SC*.
|-l <noise_threshold>| For specifying the bound on loss function for noisy data, default is *0* for perfect classification.	
|-h | Outputs the help.


### For generating samples from LTL formulas

For generating benchmarks from a given set of LTL formula, we rely on a python package LTLf2DFA that uses [MONA](https://www.brics.dk/mona/) in its backend. 
As a result, one needs to install MONA first in order to be able to use this procedure (instructions can be found in the MONA website).

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