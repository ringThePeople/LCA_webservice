import pandas as pd
import random

max_x_pos = 10.0
max_y_pos = 30.0

def get_first_order_node_position(first_adj,node_position):
    first_effected_edges = list(first_adj[first_adj==1].stack().index)
    if len(first_effected_edges)>=1:
        first_effected_source_nodes = [node_tuple[0] for node_tuple in first_effected_edges]
        first_effected_tarted_nodes = [node_tuple[1] for node_tuple in first_effected_edges]
        first_effected_source_nodes = list(set(first_effected_source_nodes).difference(set(first_effected_tarted_nodes)))

    else:
        print('No 1 in first adj')
        
        #Get any genes
        first_effected_source_nodes = first_adj.columns.tolist()[0:2]

    for i,first_effected_source_node in enumerate(first_effected_source_nodes):
        if first_effected_source_node not in node_position:
            node_position[first_effected_source_node] = tuple([ (i+1)*(max_x_pos / (len(set(first_effected_source_nodes))+1)) ,max_y_pos])

    # for i, first_effected_tarted_node in enumerate(first_effected_tarted_nodes):
    #     if first_effected_tarted_node not in node_position:
    #         node_position[first_effected_tarted_node] = tuple([ (i+1)*(max_x_pos / len(set(first_effected_tarted_nodes))+1) ,max_y_pos-1])
    return node_position


def get_remaining_node_position(remaining_nodes, node_position):
    layout_grid_rowlen = 3
    layout_grid_shift_prop = 0.2
    pos_num = 0
    tmp_max_x_pos = 0.0
    tmp_max_y_pos = 0.0
    print "REMAIN NODES:"
    print remaining_nodes
    for remain_node in remaining_nodes:
        if remain_node not in node_position:
            if random.random() < layout_grid_shift_prop:
                pos_num += 1
            grid_y = int(pos_num / float(layout_grid_rowlen)) + 1
            grid_x = pos_num % layout_grid_rowlen
            #print remain_node,"(",grid_x,", ",grid_y,")"
            node_position[remain_node] = (random.uniform(grid_x, grid_x + 0.2), random.uniform(grid_y, grid_y + 0.2))
            #node_position[remain_node] = (grid_x, grid_y)
            pos_num += 1
        if tmp_max_x_pos < node_position[remain_node][0]:
            tmp_max_x_pos = node_position[remain_node][0]
        if tmp_max_y_pos < node_position[remain_node][1]:
            tmp_max_y_pos = node_position[remain_node][1]

    for remain_node in remaining_nodes:
        tmp_x, tmp_y = node_position[remain_node]
        tmp_x = tmp_x / tmp_max_x_pos * max_x_pos
        tmp_y = tmp_y / tmp_max_y_pos * (max_y_pos - 4.5)
        node_position[remain_node] = (tmp_x, tmp_y)

    return node_position


def arrange_node_position(adj_list):
    node_position ={}
    nodes = set(adj_list[0].index)

    #first adj arrange
    first_adj  = adj_list[0]

    node_position = get_first_order_node_position(first_adj,node_position)

    #caculate the remaining nodes
    remaining_nodes = [node for node in nodes if node not in node_position.keys()]

    node_position = get_remaining_node_position(remaining_nodes,node_position)
    return node_position





if __name__ == '__main__':
    print "arrangement"
    # adj1 = pd.DataFrame([[0,0,1,0],[1,0,0,0],[0,0,0,0],[0,0,0,0]],index=['a','b','c','d'],columns=['a','b','c','d'])
    # adj2 = pd.DataFrame([[0,0,0,1],[0,0,1,0],[1,0,0,0],[0,0,1,0]],index=['a','b','c','d'],columns=['a','b','c','d'])
    # adj3 = pd.DataFrame([[0,0,1,0],[0,0,0,1],[1,0,0,0],[1,0,0,0]],index=['a','b','c','d'],columns=['a','b','c','d'])
    # adj4 = pd.DataFrame([[0,0,0,1],[1,0,0,0],[0,1,0,0],[1,0,0,0]],index=['a','b','c','d'],columns=['a','b','c','d'])

    # adj_list = [adj1, adj2, adj3,adj4]
    # print arrange_node_position(adj_list)