import pandas as pd
import numpy as np
import genie3
import repack

def run(TS_data,gene_names, _options, sp, ep):
	tool_name = _options['tool']
	period_info = _options['period']
	res_adj = []

	if period_info['type'] == 'at_once':
		# print "====_data in hub====", _data
		# adj = genie3.run_GENIE3(TS_data)
		adj = genie3.run_GENIE3(TS_data, gene_names=gene_names)
		twocol = repack.adj2twocol(adj)
		#print "twocol", twocol
		#print "type", type(twocol)
		return twocol
		print "whole data will be analyzed"
	
	elif (period_info['type'] == 'available') or (period_info['type'] == 'selective') :
		#adj = genie3.run_GENIE3(TS_data,gene_names =gene_names,ntrees=ntrees, start_point=sp, ep)
		
		adj = genie3.run_GENIE3(TS_data, gene_names=gene_names,start_point = sp ,end_point = ep)
		if (adj.ix[0][0] is None):
			return "None"
		twocol = repack.adj2twocol(adj)
		return twocol

	else:
		raise ValueError("period_info['type'] error")


	# elif period_info['type'] == 'selective':
	# 	#adj = genie3.run_GENIE3(TS_data, sp, ep)
	# 	adj = genie3.run_GENIE3(TS_data, gene_names=gene_names,start_point = sp ,end_point = ep)
	# 	if (adj.ix[0][0] is None):
	# 		return "None"
	# 	twocol = repack.adj2twocol(adj)
	# 	return twocol

	# 	print "selective periods analysis are on process"