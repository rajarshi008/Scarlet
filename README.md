## Collab (Tentative)

We solve the problem of learning LTL formulas from a sample consisting of traces partitioned into positive and negative. Most previous approaches that use enumeration over all LTL formulas to search for concise ones consistent with the sample checking consistency with the sample. Unlike other methods we essentially enumerate subsequences from the traces in the sample from which LTL formulas can be generated in a straightforward manner.

---

## Setup
- setup a python3 virtual environment using `virtualenv -p python3 venv`.
- activate the virtual environment created above using `source venv/bin/activate`.
- run `pip install -r requirements.txt` to install all necessary python dependencies.


## How to run:

For running Collab, run `python run_tests`. By default, this will run Collab on `dummy.trace`. You can run Collab with a variety of arguments that are listed below:

|Argument        |Meaning
|----------------|------------------------------
|-i \<file_name>| For specifying the path of the input file.
|-v | For output a detailed log of Collab's execution
|-vv | For output a even more detailed log of Collab's execution
|-t <timeout>| For specifying the time duration for which Collab is allowed to run (it will return the best formula it has found till then)
|-o <result_file_name>| For specifying the name of the output csv file
|-h | Outputs the help.


### Input format:

The input files consist of traces separated as positives and negatives, separated by `---`.
Each trace is a sequence of letter separated by `;`. Each letter represents the truth value of atomic propositions.
A example of a trace is `1,0,1;0,0,0` which consists of two letters each of which define the values of three propositions (by deafult consider to be `p,q,r`). 



### Generating Traces

For generating traces, one needs to run `python genBenchmarks.py`. By default, this generates traces that are consistent with the formulas provided in `formulas.txt`. You can run `genBenchmarks.py` with the following arguments:

|Argument        |Meaning
|----------------|------------------------------
|--formula_file <file_name>| For specifying the file containing all of the formulas (in prefix notation).
|--operators <list_of_operators>| For specifying the operators to be used during the execution of Collab.
|--size <list_of_tuple>| List of sample_size, i.e., number of positive traces and number of negative traces (separated by comma) in each sample.  
|--lengths <list_of_tuple>| For specifying the length range for each trace in the samples 
|-o <output_folder>| For specifying the name of the folder in which samples are generated.
|-h | Outputs the help.


<!---
### Large-scale Testing

Use `python queue_maker.py` to run a solver on a whole benchmark on a Redis server.
You can run `queue_maker` with the following arguments:


|Argument        |Meaning
|----------------|------------------------------
|-if \<foldername>| For specifying the folder containing the input files
|-t <timeout>| For specifying the time duration for which Collab is allowed to run
|-o <resultfilename>| For specifying the name of the output csv file
|-h | Outputs the help.


Then use `python queue_maker.py --compile` to compile all the results.-->
