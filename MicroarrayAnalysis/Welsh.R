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
affy_raw = read.affy()

# get pheno data from covdesc file
pd = read.table("covdesc", sep = "\t", header = TRUE)
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

# combine treatment and time
# set up design matrix
treatment = pd$TreatTime
design = model.matrix(~0 + treatment)
colnames(design) = gsub("treatment", "", colnames(design))
design

fit = lmFit(select_data, design)
# rows of select data are genes; columns are samples in same order as phenodata (pd)
# rows of design are samples (corresponding to columns of select data)

# check correspondence
pd[design[,"TGFb_90"] == 1, c("Treatment", "Time")]
pd[design[,"Control_30"] == 1, c("Treatment", "Time")] # etc

# make contrast matrix
cont_mat  = makeContrasts(TGFb_15-Control_15,
                          TGFb_30-Control_30,
                          TGFb_60-Control_60,
                          TGFb_90-Control_90,
                          TGFb_120-Control_120,
                          TGFb_150-Control_150,
                          TGFb_180-Control_180,
                          none_180-none_0, levels=colnames(design))

# get contrasts from linear model fit
fit2 = contrasts.fit(fit, contrasts=cont_mat)
# get moderated statistics
fit2 = eBayes(fit2)

degs_15 = topTable(fit2, coef="TGFb_15 - Control_15", number=nrow(select_data), adjust.method="BH", sort.by="logFC", p.value=0.05, lfc=log2(2))
degs_30 = topTable(fit2, coef="TGFb_30 - Control_30", number=nrow(select_data), adjust.method="BH", sort.by="logFC", p.value=0.05, lfc=log2(2))
degs_60 = topTable(fit2, coef="TGFb_60 - Control_60", number=nrow(select_data), adjust.method="BH", sort.by="logFC", p.value=0.05, lfc=log2(2))
degs_90 = topTable(fit2, coef="TGFb_90 - Control_90", number=nrow(select_data), adjust.method="BH", sort.by="logFC", p.value=0.05, lfc=log2(2))
degs_120 = topTable(fit2, coef="TGFb_120 - Control_120", number=nrow(select_data), adjust.method="BH", sort.by="logFC", p.value=0.05, lfc=log2(2))
degs_150 = topTable(fit2, coef="TGFb_150 - Control_150", number=nrow(select_data), adjust.method="BH", sort.by="logFC", p.value=0.05, lfc=log2(2))
degs_180 = topTable(fit2, coef="TGFb_180 - Control_180", number=nrow(select_data), adjust.method="BH", sort.by="logFC", p.value=0.05, lfc=log2(2))
degs_none = topTable(fit2, coef="none_180 - none_0", number=nrow(select_data), adjust.method="BH", sort.by="logFC", p.value=0.05, lfc=log2(2))

rownames(degs_15) %in% rownames(degs_30)
rownames(degs_30) %in% rownames(degs_60)
rownames(degs_60) %in% rownames(degs_90)
rownames(degs_90) %in% rownames(degs_120)
rownames(degs_120) %in% rownames(degs_150)
rownames(degs_150) %in% rownames(degs_180)

# add annotation
degs_30 = merge(anno_df, degs_30, by = "row.names")
degs_30 = degs_30[, !(colnames(degs_30) %in% c("Row.names", "entrez"))]
# sort by absolute fold change
degs_30 = degs_30[order(abs(degs_30$logFC), decreasing = TRUE),]


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


