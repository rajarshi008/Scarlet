
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
    affiliation: 3
  - name: Daniel Neider
    orcid: 0000-0001-9276-6342
    affiliation: 4
affiliations:
 - name: University of Antwerp, Antwerp, Belgium
   index: 1
 - name: CNRS, LaBRI and Universit´e de Bordeaux, France
   index: 2
 - name: Max Planck Institute for Software Systems, Kaiserslautern, Germany
   index: 3
 - name: Carl von Ossietzky Universität Oldenburg, Oldenburg, Germany
   index: 4
date: 26 July 2022
bibliography: paper.bib
---

# Summary

Linear Temporal Logic (LTL) is a prominent logic for specifying temporal properties over infinite traces, and recently introduced over finite traces. It has become a de facto standard in many fields such as model checking, program analysis, and motion planning for robotics. Over the past five to ten years learning temporal logics (of which LTL is the core) has become an active research area and identified as an important goal in artificial intelligence: it formalises the difficult task of building explainable models from data. Indeed LTL formulas are typically easy to interpret by human users and therefore useful as explanations. The variable free syntax of LTL and its natural inductive semantics make LTL a natural target for building classifiers separating positive from negative traces.

# Statement of need

The fundamental problem solved by `Scarlet` is to build an explainable model in the form of an LTL formula from a set of positive and negative traces.

`Scarlet` is a Python package offering an API for tasks related to LTL learning: 
* constructing an LTL formula from example traces
* generating traces from an LTL formula using automata-based techniques (LTLf2DFA and MONA) and random sampling

`Scarlet` additionally supports noisy data: the user can specify a noise threshold and the algorithm returns an almost separating formula with respect to that threshold.

# Key insights

A paper presenting the algorithms behind `Scarlet` was published in TACAS'2022: International Conference on Tools and Algorithms for the Construction and Analysis of Systems [@RahaRFN22]. 

We believe that the path to scalability for LTL learning is to leverage normal forms for LTL formulas and derive efficient enumeration algorithms from them. Scarlet combines two insights:

* An efficient enumeration algorithm for directed LTL formulas, which are formulas that can be evaluated only moving forward in words
* An algorithm solving the Boolean set cover problem, which constructs Boolean combination of already constructed formulas in order to separate positive and negative examples.

Evaluation experiments are presented in the paper [@RahaRFN22].

# Related works

A number of different approaches have been proposed, leveraging SAT solvers [@NeiderGavran18], automata [@Camacho_McIlraith_2019], and Bayesian inference [@ijcai2019-0776], and extended to more expressive logics such as Property Specification Language (PSL) [@RoyFismanNeider20] and Computational Tree Logic (CTL) [@EhlersGavranNeider20].

Applications include program specification [@LPB15], anomaly and fault detection [@BoVaPeBe-HSCC-2016], robotics [@ChouOB20], and many more: we refer to [@Camacho_McIlraith_2019], Section 7, for a list of practical applications.
An equivalent point of view on LTL learning is as a specification mining question. 
The ARSENAL [@GhoshELLSS16] and FRET [@GiannakopoulouP20a] projects construct LTL specifications from natural language, we refer to [@Li13d] for an overview.

The two state-of-the-art tools for learning logic formulas from examples are:
* FLIE [@NeiderGavran18] infers minimal LTL formulas using a learning algorithm that is based on constraint solving (SAT solving).
* SYSLITE [@ArifLERCT20] infers minimal past-time LTL formulas using an enumerative algorithm implemented in a tool called CVC4SY [@ReynoldsBNBT19].

Existing methods do not scale beyond formulas of small size, making them hard to deploy for industrial cases. A second serious limitation is that they often exhaust computational resources without returning any result. Indeed theoretical studies [@FijalkowLagarde21] have shown that constructing the minimal LTL formula is NP-hard already for very small fragments of LTL, explaining the difficulties found in practice.
