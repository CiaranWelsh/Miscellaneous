# Ciaran Welsh time course analysis

# Affy U219 chip

setwd("/data/customers/Welsh/")

# Affymetrix packages
library(affy)
library(affycoretools)
library(simpleaffy)
library(hgu219.db)
library(hgu219probe)
library(hgu219cdf)
# affyPLM required to interrogate normalised celfiles.gcrma
library(affyPLM)

# Annotation and modelling
library(annotate)
library(limma)

# Colour libraries and colour palette for graphics
library(RColorBrewer)
cols = brewer.pal(8, "Set1")

# read CEL files and phenotypic data with simpleaffy
affy_raw = read.affy(covdesc = "covdesc_time_course")

# get pheno data from covdesc file
pd = read.table("covdesc_time_course", sep = "\t", header = TRUE)
pd$TreatTime = as.factor(paste(pd$Treatment, pd$Time, sep ="_"))

# normalise
affy_norm = rma(affy_raw)

# QC pre- and post- normalisation
boxplot(affy_raw, col=cols)
boxplot(affy_norm, col=cols)
hist(affy_raw, col=cols)
hist(affy_norm, col=cols)

# Perform probe-level metric calculations on the CEL files:
affy_qc = fitPLM(affy_raw)

image(affy_qc, which=1, add.legend=TRUE)
image(affy_qc, which=5, add.legend=TRUE)

# Get expression data as an object
eset = exprs(affy_norm)

# Sample distance dendrogram
distance = dist(t(eset),method="euclidian")
clusters = hclust(distance, method="complete")
plot(clusters)
# Sample distances by treatment and time
eset2 = eset
colnames(eset2) = paste(pd$Treatment, pd$Time, sep = "_")
distance = dist(t(eset2),method="euclidian")
clusters = hclust(distance, method="complete")
plot(clusters)

# PCA plot by treatment
plotPCA(affy_norm, groups = as.numeric(pd$Treatment), groupnames = levels(pd$Treatment),
        main = "Principal Components Plot: Treatments")

# PCA plot by replicate
plotPCA(affy_norm, groups = pd$Replicate, groupnames = levels(as.factor(pd$Replicate)),
        main = "Principal Components Plot: Replicates")


# PCA plot by treatment and time
plotPCA(affy_norm, groups = as.numeric(pd$TreatTime), groupnames = levels(pd$TreatTime),
        main = "Principal Components Plot: Treatment and Time", outside = TRUE)



# Probe filtering (remove probes with low variance or low signal across samples)
affy_filtered = nsFilter(affy_norm, require.entrez=FALSE, remove.dupEntrez=FALSE)

# check filter log
affy_filtered$filter.log

# Get expression data post-filtering
affy_filtered_data = affy_filtered$eset

# proceed with filtered probes
select_data = exprs(affy_filtered_data)
probe_list = rownames(select_data)

# get annotation
symbol = getSYMBOL(probe_list, "hgu219.db")
name = unlist(lookUp(probe_list, "hgu219.db", "GENENAME"))
entrez = unlist(lookUp(probe_list, "hgu219.db", "ENTREZID"))
anno_df = data.frame(ID = probe_list, symbol, name, entrez)

# time course analysis

library(splines)
X = ns(pd$Time, df = 3)

Group = pd$Treatment
design = model.matrix(~Group*X)
tc_fit = lmFit(select_data, design)
tc_fit = eBayes(tc_fit)

out = topTable(tc_fit, coef = 6:8, number = nrow(select_data))

# add annotation
degs = merge(anno_df, out, by = "row.names")
degs = degs[, !(colnames(degs) %in% c("Row.names", "entrez"))]
# apply F statistic cut-off of 100
degs = degs[degs$F >= 100, ]
# sort by F statistic
degs = degs[order((degs$F), decreasing = TRUE),]


# 1. Background Correction
# 2. Normalization
# 3. Summarization
# in the case of rma()
# step 1 is a convolution model
# step 2 is quantile normalization
# step 3 is a robust multichip model fit using median polish,
# in the case of gcrma()
# step 1 is a based on a model using GC content
# step 2 is quantile normalization
# step 3 is a robust multichip model fit using median polish


