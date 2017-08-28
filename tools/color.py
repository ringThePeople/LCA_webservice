from scipy import stats
import pandas as pd
import numpy as np

# ts_file = "./data/Spellman_cdc15.txt"
# df = pd.read_csv(ts_file,sep="\t")

# thr = 0.1

#normalized df
# for gene in df.columns:
#     normalized_df = df.copy(deep=True)
#     normalized_df[gene] = (normalized_df[gene] - normalized_df[gene].mean())/normalized_df[gene].std()


def get_over_under_exp_genes(exp_df,thr):
    over_exp_genes = []
    under_exp_genes = []

    for gene in exp_df.columns:
        exp =  exp_df.loc[:,gene]
        x = range(1,len(exp)+1)
        slope,intercept,r_value,p_value, std_err = stats.linregress(x,exp)
        if p_value <= thr:
            if slope<0:
                under_exp_genes.append(gene)
            elif slope>0:
                over_exp_genes.append(gene)
            else:
                raise ValueError('slope is 0')

    return over_exp_genes, under_exp_genes