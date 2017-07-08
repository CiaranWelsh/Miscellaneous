# Miscellaneous
Collection of subprojects that are not big enough to warrant their own repository 


# LASSO Regression
In this work I am trying to use time course expression data from WaferGen and Microarray to produce a correlation matrix for each gene in our set of genes. I use a lasso regression model to select features with a non-zero coefficient which are then candidates for regulators. A jupyter notebook provides implements the methods which utilie sklearn, a python package for machine learning. 

# RPPA Analysis
Here I've written a script that can be used to normalize RPPA data. It'll need adapting for each experiment by modifying the path to the data file aswell as graph labels. This script is intended to replace RPPA normalization stuff I've done previously as simpler is better and realistically a new class structure is just over complicating the problem - all the tools needed to do the normalization already exist so there's no need to write more. The script is more of a template for adaption. 