import json
from numpy import *
import csv
import berexapi as bex
from pandas import Series, DataFrame
import pandas as pd
import tools.color as toolcolor
import tools.arrange as toolarrange
import numpy as np
import itertools
import tools.repack as toolrepack
import tools.genie3 as toolgenie3

ERROR_CODE = ["", 1]

def is_valid_form(_data):
	return 0

def timeseriesanalysis(_tsdata):
	# expand with analysis tool
	# import other .py file
	return _tsdata

def tsv2json_n2(_tsvdata, _bexdata, _validpairs, over_list, under_list, bex_all, all_vp, position_list, graph_count, totalwidth, totalheight):
	_line = _tsvdata.split('\n')
	graphdict = {'nodes':[], 'edges':[]}
	
	for eachline in _line[1:]:
		if(len(eachline)==0):
			continue
		e1, e2 = eachline.strip().split('\t')
		if((e1,e2) in bex_all):
			bex_all.remove((e1,e2))

		# handling edge style if in berex
		if((e1,e2) in _bexdata):
			for v_ps in _validpairs:
				if v_ps['source'] == e1 and v_ps['target'] == e2:
					graphdict['edges'].append({'data':{'source': e1, 'target': e2, 'interaction':v_ps['interaction'], 'dbsource':v_ps['dbsource']}, 'style':{'line-color': '#c0c0c0', 'width': 6, 'line-style': 'solid'}})
					print "e1", e1, "e2", e2
					break
			continue

		graphdict['edges'].append({'data':{'source': e1, 'target': e2}, 'style':{'line-style': 'dashed'} })

	x_list = []
	y_list = []
	for eachnode in _line[0].strip().split(';'):
		(x,y) = position_list[eachnode]
		x_list.append(x)
		y_list.append(y)

	x_length = max(x_list)
	y_length = max(y_list)

	# for eachnode in _line[0].strip().split(';'):
	# 	(x,y) = position_list[eachnode]
	# 	xp = x*100.0/x_length
	# 	yp = y*100.0/y_length
		
	# 	if(eachnode in over_list):
	# 		graphdict['nodes'].append({'data':{'id':eachnode, 'col':'#c7030a', 'x':xp, 'y':yp}})
	# 		continue
	# 	if(eachnode in under_list):
	# 		graphdict['nodes'].append({'data':{'id':eachnode, 'col':'#69bc39', 'x':xp, 'y':yp}})
	# 		continue
	# 	graphdict['nodes'].append({'data':{'id':eachnode, 'col':'#ffff00', 'x':xp, 'y':yp}})
	wm = 0.22*totalwidth
	hm = 0.64 * totalheight

	for eachnode in _line[0].strip().split(';'):
		(x,y) = position_list[eachnode]
		print "y_length", y_length, "y", y
		y = y_length - y + 2

		x = x*wm/x_length
		y = y*hm/y_length
		if graph_count == 1:
			x = x * 2

		# print "position",eachnode,"x",x,"y",y
		# print "over_list", over_list
		# print "under_list", under_list
		# print "each_node", eachnode

		if(eachnode in over_list):
			graphdict['nodes'].append({'data':{'id':eachnode, 'col':'#c7030a', 'x':x, 'y':y}})
			continue
		if(eachnode in under_list):
			graphdict['nodes'].append({'data':{'id':eachnode, 'col':'#69bc39', 'x':x, 'y':y}})
			continue

		graphdict['nodes'].append({'data':{'id':eachnode, 'col':'#ffff00', 'x':x, 'y':y}})
	return json.dumps(graphdict)

def run(file_io_list, _options):
	if not file_io_list:
		return ERROR_CODE
	if is_valid_form(file_io_list):
		return ERROR_CODE
	uw,uh = _options['size']
	totalwidth = float(uw)
	totalheight = float(uh)

	TS_arrays =[]
	for file_io in file_io_list:
		TS_df = pd.read_csv(file_io,sep="\t")
		gene_names = TS_df.columns.tolist()
		TS_array = TS_df.as_matrix()
		TS_arrays.append(TS_array)

	TS_data = np.asarray(TS_arrays)

	table_len = int(TS_data[0].shape[0])
	print table_len

	period_info = _options['period']
	ntree = int(period_info['ntree'])
	threshold = float(period_info['threshold'])

	graph_count = 1

	#temp 

	normalized_df = pd.DataFrame(np.copy(TS_data[0]),columns=gene_names)
	#normalized_df=df.copy(deep=True)
	for gene in gene_names:
		normalized_df[gene] = (normalized_df[gene]-normalized_df[gene].mean())/(normalized_df[gene].std())

	thr = 0.05
	over_exp_genes , under_exp_genes = toolcolor.get_over_under_exp_genes(normalized_df, thr=thr)

	print "over_ list",over_exp_genes
	print "under_ list", under_exp_genes

	sp = 1
	i = 0
	_jsons = []
	_2col_list = []
	v_p_list = []
	bex_to_edgelist_list = []
	over_exp_genes_list = []
	under_exp_genes_list = []
	#berex request
	all_edge_pos_tuple_list = list(itertools.permutations(gene_names,2))
	all_edge_pos = [{'source':edge_pos[0],'target':edge_pos[1]} for edge_pos in all_edge_pos_tuple_list]

	all_vp = bex.get_berexedges(all_edge_pos)
	bex_all = bex.berexresult_to_edgelist(all_vp)

	if period_info['type'] == 'at_once':
		graph_count = 1
		
		_adj = toolgenie3.run_GENIE3(TS_data, gene_names=gene_names, ntrees=ntree, threshold=threshold)
		tcol = toolrepack.adj2twocol(_adj)

		tcol_rows = [row for row in tcol.split('\n')]

		#Inferece edges 
		list_nodes = []
		for ii in range(1, len(tcol_rows)):
			if(len(tcol_rows[ii])==0):
				continue
			source_target_dic = {}
			temp_row = tcol_rows[ii].split('\t')
			source_target_dic['source'] = temp_row[0]
			source_target_dic['target'] = temp_row[1]
			list_nodes.append(source_target_dic)

		v_p = bex.get_berexedges(list_nodes)
		bex_to_edgelist = bex.berexresult_to_edgelist(v_p)
		
		#calculate position value
		_line = tcol.split('\n')
		all_node = []
		for eachnode in _line[0].strip().split(';'):
			all_node.append(eachnode)
		adj = pd.DataFrame(0,index=all_node,columns=all_node)
		for eachline in _line[1:]:
			#e1 is source,  e2 is target
			if(len(eachline)==0):
				continue
			e1, e2 = eachline.strip().split('\t')
			adj[e2][e1] = 1

		adj_list = []
		adj_list.append(adj)
		position_list = toolarrange.arrange_node_position(adj_list)

		_jsons.append(tsv2json_n2(tcol, bex_to_edgelist, v_p, over_exp_genes, under_exp_genes, bex_all, all_vp, position_list, graph_count, totalwidth, totalheight))
	

		
	elif period_info['type'] == 'available':
		period_val = int(period_info['value'])
		adj_list = []
		# graphs are more than one.
		if (sp+(2 * period_val)-1 < table_len):
			graph_count = 2

		print "period_val :", period_val
		while (sp+((i+1) * period_val)-1 <= table_len) :
			print "interation : " , i+1 
			start_t = sp+ (i *period_val)
			end_t = sp+((i+1) * period_val)-1
			# df_2=df.copy(deep=True)

			df = pd.DataFrame(np.copy(TS_data[0]),columns=gene_names)
			normalized_df=df.iloc[start_t:(end_t+1),:]
			for gene in gene_names:
				normalized_df[gene] = (normalized_df[gene]-normalized_df[gene].mean())/(normalized_df[gene].std())

			thr = 0.05
			over_exp, under_exp = toolcolor.get_over_under_exp_genes(normalized_df, thr=thr)
			over_exp_genes_list.append(over_exp)
			under_exp_genes_list.append(under_exp)

			_adj = toolgenie3.run_GENIE3(TS_data, gene_names=gene_names,start_point = start_t ,end_point = end_t, ntrees=ntree, threshold=threshold)
			_2col_list.append(toolrepack.adj2twocol(_adj))
			
			if _2col_list[i][0:4] == 'None':
				i = i+1
				continue
			try:
				tcol = [row for row in _2col_list[i].split('\n')]
				
				list_nodes = []
				for ii in range(1, len(tcol)):
					if(len(tcol[ii])==0):
						continue
					source_target_dic = {}
					temp_row = tcol[ii].split('\t')
					source_target_dic['source'] = temp_row[0]
					source_target_dic['target'] = temp_row[1]
					list_nodes.append(source_target_dic)
				v_p_list.append(bex.get_berexedges(list_nodes))
				bex_to_edgelist_list.append(bex.berexresult_to_edgelist(v_p_list[i]))
				
			except:
				i = i + 1
				continue
			#calculate position value
			_line = _2col_list[i].split('\n')
			all_node = []
			for eachnode in _line[0].strip().split(';'):
				all_node.append(eachnode)
			adj = pd.DataFrame(0,index=all_node,columns=all_node)
			for eachline in _line[1:]:
				if(len(eachline)==0):
					continue
				#e1 is source,  e2 is target
				e1, e2 = eachline.strip().split('\t')
				adj[e2][e1] = 1
			adj_list.append(adj)

			i = i + 1 #
		position_list = toolarrange.arrange_node_position(adj_list)

		for i in range(0, len(_2col_list)):
			if _2col_list[i] is None:
				continue
			
			_jsons.append(tsv2json_n2(_2col_list[i], bex_to_edgelist_list[i], v_p_list[i], over_exp_genes_list[i], under_exp_genes_list[i], bex_all, all_vp, position_list, graph_count, totalwidth, totalheight))
		#end - type : 'available'
		
	elif period_info['type'] == 'selective':
		period_string_list = (period_info['selective_form']).split(';')
		start_point_list = (period_string_list[0].split(','))[0:-1]
		# each period -> each end point 
		each_period_list = (period_string_list[1].split(','))[0:-1]
		if(len(start_point_list) == 0):
			print "Selective Period input is Empty"
		#graphs are more than one
		if(len(start_point)>1):
			graph_count = 2

		adj_list = []
		for i in range(0, len(start_point_list)):
			if(len(start_point_list[i]) == 0):
				print  i+1, "th period's Start Point is Empty" 
				continue
			start_point = int(start_point_list[i])

			try:
				each_period = int(each_period_list[i])
			except:
				print i+1, "th wrong period"
				continue
			# this method : each period operation
			# end_point = start_point + each_period - 1

			# change selective system
			end_point = each_period
			if(end_point <= table_len):
				print "iteration : ", i+1
				df = pd.DataFrame(np.copy(TS_data[0]),columns=gene_names)
				normalized_df=df.iloc[start_point:(end_point+1),:]
			for gene in gene_names:
				normalized_df[gene] = (normalized_df[gene]-normalized_df[gene].mean())/(normalized_df[gene].std())
			thr = 0.05		
			over_exp , under_exp = toolcolor.get_over_under_exp_genes(normalized_df, thr=thr)
			over_exp_genes_list.append(over_exp)
			under_exp_genes_list.append(under_exp)
			_adj = toolgenie3.run_GENIE3(TS_data, gene_names=gene_names,start_point = start_point ,end_point = end_point, ntrees=ntree, threshold=threshold)
			_2col_list.append(toolrepack.adj2twocol(_adj))


			if _2col_list[i] is None:
				continue
			try:
				tcol = [row for row in _2col_list[i].split('\n')]
				
				list_nodes = []
				for ii in range(1, len(tcol)):
					if(len(tcol[ii])==0):
						continue
					source_target_dic = {}
					temp_row = tcol[ii].split('\t')
					source_target_dic['source'] = temp_row[0]
					source_target_dic['target'] = temp_row[1]
					list_nodes.append(source_target_dic)
				v_p_list.append(bex.get_berexedges(list_nodes))
				bex_to_edgelist_list.append(bex.berexresult_to_edgelist(v_p_list[i]))
			
			except:
				continue
			_line = _2col_list[i].split('\n')
			all_node = []
			for eachnode in _line[0].strip().split(';'):
				all_node.append(eachnode)
			adj = pd.DataFrame(0,index=all_node,columns=all_node)
			for eachline in _line[1:]:
				if(len(eachline)==0):
					continue
				#e1 is source,  e2 is target
				e1, e2 = eachline.strip().split('\t')
				adj[e2][e1] = 1
			adj_list.append(adj)
		position_list = toolarrange.arrange_node_position(adj_list)
		for i in range(0, len(_2col_list)):
			if _2col_list[i] is None:
				continue
			try:
				_jsons.append(tsv2json_n2(_2col_list[i], bex_to_edgelist_list[i], v_p_list[i], over_exp_genes_list[i], under_exp_genes_list[i], bex_all, all_vp, position_list, graph_count, totalwidth, totalheight))
			except:
				print "error detection"
				continue

	return [_jsons, 0]



if __name__ == '__main__':
	print "SOMETHING HERE"
