
---
title: 'Scarlet: Scalable Anytime Algorithms for Learning Fragments of Linear Temporal Logic'
tags:
  - Python
  - linear temporal logic (LTL)
  - passive learning
  - specification mining
  - formal methods
authors:
  - name: Ritam Raha
    orcid: 0000-0003-1467-1182
    equal-contrib: true
    corresponding: true # (This is how to denote the corresponding author)
    affiliation: "1, 2" # (Multiple affiliations must be quoted)
  - name: Rajarshi Roy
    orcid: 0000-0002-0202-1169
    corresponding: true # (This is how to denote the corresponding author)
    equal-contrib: true # (This is how you can denote equal contributions between multiple authors)
    affiliation: 3
  - name: Nathanaël Fijalkow
    orcid: 0000-0002-6576-4680
    affiliation: 2
  - name: Daniel Neider
    orcid: 0000-0001-9276-6342
    affiliation: 4
affiliations:
 - name: University of Antwerp, Antwerp, Belgium
   index: 1
 - name: CNRS, LaBRI and Université de Bordeaux, France
   index: 2
 - name: Max Planck Institute for Software Systems, Kaiserslautern, Germany
   index: 3
 - name: Carl von Ossietzky Universität Oldenburg, Oldenburg, Germany
   index: 4
date: 26 July 2022
bibliography: paper.bib
---

# Summary

In the past few years, incorporating data-driven AI techniques in system design has become mainstream, almost in all branches of science and technology.
Typically, systems powered by AI tend to be rather complex, far beyond human understanding.
Naturally, one cannot always develop trust in such complex, so-called black-box systems, restricting their widespread use in safety-critical domains.

To generate trust in systems, a standard approach in Explainable AI is to build simple explanations using human-understandable models.
A number of recent works [@NeiderGavran18] [@Camacho_McIlraith_2019] [@RoyFismanNeider20] have identified models in temporal logic to be both formal and explainable.
Among temporal logics---Linear Temporal Logic (LTL)---arguably the most widely used temporal logic, has received particular focus due to its ease-of-use.
LTL is in fact a de facto standard in several fields of computer science, including model checking, program analysis, and motion planning for robotics.

`Scarlet` is one of the most competitive tools for learning explainable models in LTL [@RahaRFN22].
To learn the explainable models, it relies on positive (or desirable) and negative (or undesirable) executions of the system under consideration.
Based on the executions, it learns a concise model in LTL that is consistent with the given executions.

Let us consider a concrete example to understand `Scarlet`'s functioning.
Consider a robot that has been designed to collect wastebin contents in an office-like environment.
For the sake of the example, in this environment, let there be an office o with a wastebin, a hallway h, and a container c to accumulate the waste.
The following could be the possible executions of the robot:

h.h.h.h.o.h.c.h
h.h.h.h.h.c.h.o.h.h

Let the first execution be positive since the robot first collects waste from the office and then accumulates in the container.
Also, let the second execution be negative since the robot tries to accumulate the waste in the container even before it collects from the office.
From these executions, `Scarlet` learns a model `F(o and FX c)`, where the `F`-operator stands for "finally" and `X`-operator stands for "next".
The model, in simple words, expresses that: eventually, the robot should visit the office and then, at a later point visit the container. 


# Statement of need

The fundamental problem solved by `Scarlet` is to build an explainable model in the form of an LTL formula from a set of positive and negative execution traces.

`Scarlet` is a tool built entirely in Python 3. It can be run using its command-line features or its Python API hosted in PyPi. Its main capabilities include:

* construction of an LTL formula from execution traces,
* generation of execution traces from an LTL formula for testing LTL learning algorithms (using automata-based techniques, such as LTLf2DFA and MONA, and random sampling).

`Scarlet` additionally supports noisy data: the user can specify a noise threshold (between zero and one, zero for perfect classification) and the algorithm returns an almost separating formula with respect to that threshold.

# Key insights

A paper presenting the algorithms behind `Scarlet` was published in TACAS'2022: International Conference on Tools and Algorithms for the Construction and Analysis of Systems [@RahaRFN22]. 

We believe that the path to scalability for learning models in LTL is to leverage normal forms for LTL formulas and derive efficient enumeration algorithms from them. `Scarlet` combines two insights:

* An efficient enumeration algorithm for directed LTL formulas, which are formulas that can be evaluated only moving forward in execution traces,
* An algorithm solving the Boolean set cover problem, which constructs Boolean combinations of already constructed formulas in order to separate positive and negative execution traces.

Evaluation experiments are presented in the paper [@RahaRFN22].

# Related works

For learning models in LTL, a number of different approaches have been proposed, leveraging SAT solvers [@NeiderGavran18], automata [@Camacho_McIlraith_2019], and Bayesian inference [@ijcai2019-0776]. In fact, there are approaches for more expressive logics such as Property Specification Language (PSL) [@RoyFismanNeider20] and Computational Tree Logic (CTL) [@EhlersGavranNeider20].

Applications of LTL learning include program specification [@LPB15], anomaly and fault detection [@BoVaPeBe-HSCC-2016], robotics [@ChouOB20], and many more: we refer to [@Camacho_McIlraith_2019], Section 7, for a list of practical applications.
An equivalent point of view on LTL learning is as a specification mining question. 
The ARSENAL [@GhoshELLSS16] and FRET [@GiannakopoulouP20a] projects construct LTL specifications from natural language; we refer to [@Li13d] for an overview.

The two state-of-the-art tools for learning logic formulas from examples are:

* FLIE [@NeiderGavran18] infers minimal LTL formulas using a learning algorithm that is based on constraint solving (SAT solving).
* SYSLITE [@ArifLERCT20] infers minimal past-time LTL formulas using an enumerative algorithm implemented in a tool called CVC4SY [@ReynoldsBNBT19].

Existing methods do not scale beyond formulas of small size, making them hard to deploy for industrial cases. A second serious limitation is that they often exhaust computational resources without returning any results. Indeed theoretical studies [@FijalkowLagarde21] have shown that constructing the minimal LTL formula is NP-hard already for very small fragments of LTL, explaining the difficulties found in practice.

# Acknowledgments

This project was funded by the FWO G030020N project `SAILor` and Deutsche Forschungsgemeinschaft (DFG) grant no. 434592664.


# References
