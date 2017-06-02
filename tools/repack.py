import pandas as pd
import numpy as np

def adj2twocol(_adj):
	node_info = ""
	edge_info = ""
	idx_list = _adj.index
	col_list = _adj.columns.values
	# print _adj.loc[idxs[0]][cols[1]]

	for i in idx_list:
		if len(node_info):
			node_info = node_info + ';' + i
		else:
			node_info = i
		for j in col_list:
			if _adj.loc[i][j] > 0.9:
				edge_info = edge_info + '\n' + i + '\t' + j
	node_info = node_info.strip()
	edge_info = edge_info.strip()
	return node_info + '\n' + edge_info


if __name__ == "__main__":
	df = pd.DataFrame(data=np.array([[1,2],[3,4]]),columns=['A','B'],index=['AA','BB'], dtype=np.float32)
	print df
	adj2twocol(df)