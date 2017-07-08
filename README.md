# Miscellaneous
Collection of subprojects that are not big enough to warrant their own repository 


# LASSO Regression
In this work I am trying to use time course expression data from WaferGen and Microarray to produce a correlation matrix for each gene in our set of genes. I use a lasso regression model to select features with a non-zero coefficient which are then candidates for regulators. A jupyter notebook provides implements the methods which utilie sklearn, a python package for machine learning. 

# RPPA Analysis
Here I've written a script that can be used to normalize RPPA data. It'll need adapting for each experiment by modifying the path to the data file aswell as graph labels. This script is intended to replace RPPA normalization stuff I've done previously as simpler is better and realistically a new class structure is just over complicating the problem - all the tools needed to do the normalization already exist so there's no need to write more. The script is more of a template for adaption. 

# SBConcat_combo
This is a piece of work I did a long time ago. The idea is to use sb_shorthand to concatonate model modules.This worked quite well and I then went on to use a matlab toolbox for optimization on the various output models. The optimization component is probably no longer needed as I can feed any models into PyCoTools but the concatonation of models for model selection is a good tool that I should remember about for my PhD. 

# Microarray analysis
These script are examples of how to assess QC for microarray data and how to extract differentially expressed genes for both time courses and non-time courses. I've not uploaded the actual data due to sensitivity reasons. 