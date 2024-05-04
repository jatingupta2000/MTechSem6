import re
import json
import os

# Reading Benchmark File
def read_benchmark(file_name):
    f = open(file_name)
    ckt = f.read()
    f.close()
    return ckt

# Retrieving DFF Input & Output
def get_dff_io(ckt):
    dff_io_map = dict()
    dff_in_set = set()
    dff_out_set = set()
    for stmt in ckt.split("\n"):
        if " = DFF(" in stmt:
            dff_in_set.add(stmt.strip().split("(")[1][:-1])
            dff_out_set.add(stmt.strip().split(" = ")[0])
            dff_io_map[stmt.strip().split(" = ")[0]] = stmt.strip().split("(")[1][:-1]
    return list(dff_in_set), list(dff_out_set), dff_io_map

# Retrieving Primary Input-Keys & Output
def get_primary_io(ckt):
    pi_set = set()
    po_set = set()
    for stmt in ckt.split("\n"):
        if "INPUT(" in stmt:
            pi_set.add(stmt.strip().split("(")[1][:-1])
        if "OUTPUT(" in stmt:
            po_set.add(stmt.strip().split("(")[1][:-1])
    return list(pi_set), list(po_set)

# Parse Circuit
def parse_circuit(ckt):
    edge_info = {}
    for i in ckt.split("\n"):
        if "=" in i:
            lhs, rhs = i.split('=')
            lhs = lhs.strip()
            rhs = rhs.strip()

            operators = ["NOR", "NOT", "OR", "NAND", "XOR", "XNOR", "AND", "BUF", "DFF"]
            for operator in operators:
                if rhs.startswith(f"{operator}(") and rhs.endswith(')'):
                    operands = rhs[len(operator) + 1:-1].split(',')
                    operands = [operand.strip() for operand in operands]
                    edge_info[lhs] = (operator,operands,i)
    return edge_info

# BFS Traversal from particular node
def bfs_traverse(node, pi, dff_output, ckt_dict):
    bfs = list()
    visited = list()
    queue = list()
    queue.append(node)
    while len(queue) > 0:
        ele = queue.pop(0)
        if ele in visited:
            continue
        elif ele in dff_output:
            visited.append(ele)
        elif ele in pi:
            visited.append(ele)
        else:
            visited.append(ele)
            bfs.append(ckt_dict[ele][-1])
            for _tmp in ckt_dict[ele][1]:
                queue.append(_tmp)
    return bfs

# BFS Traversal from particular node to principle input
def bfs_traverse_to_pi(node, pi, ckt_dict):
    bfs = list()
    visited = list()
    queue = list()
    queue.append(node)
    while len(queue) > 0:
        ele = queue.pop(0)
        if ele in visited:
            continue
        #elif ele in dff_output:
        #    visited.append(ele)
        elif ele in pi:
            visited.append(ele)
        else:
            visited.append(ele)
            bfs.append(ckt_dict[ele][-1])
            for _tmp in ckt_dict[ele][1]:
                queue.append(_tmp)
    return bfs

# Retrieving Logic Cones
def get_logic_cones(pi, po, dff_input, dff_output, ckt_dict):
    logic_cone = {}
    for _in in pi:
        logic_cone[_in] = bfs_traverse(_in, pi, dff_output, ckt_dict)
    for _out in po:
        logic_cone[_out] = bfs_traverse(_out, pi, dff_output, ckt_dict)
    for _dff_in in dff_input:
        logic_cone[_dff_in] = bfs_traverse(_dff_in, pi, dff_output, ckt_dict)
    return logic_cone

# Retrieving Logic Cones to Pi
def get_logic_cones_to_pi(pi, po, ckt_dict):
    logic_cone = {}
    for _out in po:
        logic_cone[_out] = bfs_traverse_to_pi(_out, pi, ckt_dict)
    return logic_cone

# Retrieving Logic Cones Schema
def get_logic_cone_schema(dff_input, logic_cone):
    logic_cone_schema = dict()
    for _in in dff_input:
        _cone = str(logic_cone[_in])
        _spre = re.findall(r'\bs\w*', _cone, flags=0)
        _wpre = re.findall(r'\bw\w*', _cone, flags=0)
        _keypre = re.findall(r'\bkeyinput_\w*', _cone, flags=0)
        _inpre = re.findall(r'\bin\w*', _cone, flags=0)
        _opre = re.findall(r'\bo\w*', _cone, flags=0)
        _spre.sort(reverse=True)
        _wpre.sort(reverse=True)
        _keypre.sort(reverse=True)
        _inpre.sort(reverse=True)
        _opre.sort(reverse=True)
        for _temp in _spre:
            _cone = _cone.replace(_temp, 's')
        for _temp in _wpre:
            _cone = _cone.replace(_temp, 'w')
        for _temp in _keypre:
            _cone = _cone.replace(_temp, 'k')
        for _temp in _inpre:
            _cone = _cone.replace(_temp, 'i')
        for _temp in _opre:
            _cone = _cone.replace(_temp, 'o')
        logic_cone_schema[_in] = _cone
    return logic_cone_schema

# Get Logic Cones containing key
def get_key_logic_cone(dff_input, logic_cone):
    dct = dict()
    for _in in dff_input:
        lc = str(logic_cone[_in])
        if "keyinput" in lc:
            _lst = re.findall(r'\bkeyinput_\w*', lc, flags=0)
            dct[_in] = list(set(_lst))
    return dct

def dump_initial_data_file(file_name):
    if not os.path.exists('./Resources'):
        print('Error: "Resources" folder doesn\'t exists.')
        return
    
    ckt = read_benchmark(file_name)
    with open('./Resources/ckt.json', 'w') as file:
        json.dump(ckt, file)
    dff_input, dff_output, dff_io_map = get_dff_io(ckt)
    with open('./Resources/dff_input.json', 'w') as file:
        json.dump(dff_input, file)
    with open('./Resources/dff_output.json', 'w') as file:
        json.dump(dff_output, file)
    with open('./Resources/dff_io_map.json', 'w') as file:
        json.dump(dff_io_map, file)
    pi, po = get_primary_io(ckt)
    with open('./Resources/pi.json', 'w') as file:
        json.dump(pi, file)
    with open('./Resources/po.json', 'w') as file:
        json.dump(po, file)
    ckt_dict = parse_circuit(ckt)
    with open('./Resources/ckt_dict.json', 'w') as file:
        json.dump(ckt_dict, file)
    logic_cone = get_logic_cones(pi, po, dff_input, dff_output, ckt_dict)
    with open('./Resources/logic_cone.json', 'w') as file:
        json.dump(logic_cone, file)
    key_in_logic_cone = get_key_logic_cone(dff_input, logic_cone)
    with open('./Resources/key_in_logic_cone.json', 'w') as file:
        json.dump(key_in_logic_cone, file)
    """logic_cone_schema = get_logic_cone_schema(dff_input, logic_cone)
    with open('./Resources/logic_cone_schema.json', 'w') as file:
        json.dump(logic_cone_schema, file)
    logic_cone_to_pi = get_logic_cones_to_pi(pi, po, ckt_dict)
    with open('./Resources/logic_cone_to_pi.json', 'w') as file:
        json.dump(logic_cone_to_pi, file)"""

def load_intial_data():
    with open('./Resources/ckt.json', 'r') as file:
        ckt = json.load(file)
    with open('./Resources/dff_input.json', 'r') as file:
        dff_input = json.load(file)
    with open('./Resources/dff_output.json', 'r') as file:
        dff_output = json.load(file)
    with open('./Resources/dff_io_map.json', 'r') as file:
        dff_io_map = json.load(file)
    with open('./Resources/pi.json', 'r') as file:
        pi = json.load(file)
    with open('./Resources/po.json', 'r') as file:
        po = json.load(file)
    with open('./Resources/ckt_dict.json', 'r') as file:
        ckt_dict = json.load(file)
    with open('./Resources/logic_cone.json', 'r') as file:
        logic_cone = json.load(file)
    with open('./Resources/key_in_logic_cone.json', 'r') as file:
        key_in_logic_cone = json.load(file)
    """with open('../Resources/logic_cone_schema.json', 'r') as file:
        logic_cone_schema = json.load(file)
    with open('../Resources/logic_cone_to_pi.json', 'r') as file:
        logic_cone_to_pi = json.load(file)"""
    return ckt, dff_input, dff_output, dff_io_map, pi, po, ckt_dict, logic_cone, key_in_logic_cone

def get_external_input_to_lc(dff_out_node, ckt_dict, logic_cone):
	lc = logic_cone[ckt_dict[dff_out_node][1][0]]
	extern = set()
	for stmt in lc:
		par = ckt_dict[stmt.split(' = ')[0]][1]
		for _par in par:
			if not _par.startswith('w'):
				extern.add(_par)			
	return list(extern)

def generate_register_graph(dff_output, ckt_dict, logic_cone):
	f = open('reg_graph.dot', 'w')
	f.writelines('digraph G{\n')
	f.writelines('splines=ortho\n')
	f.writelines('node [shape=rect]\n')
	for out in dff_output:
		in2lc = get_external_input_to_lc(out, ckt_dict, logic_cone)
		for _in in in2lc:
			f.writelines(str(_in + '->' + out + '\n'))
	f.writelines('}')
	f.close()

# Latency Calculation
"""def get_latency(node, pi, ckt_dict):
    final_latency = 0
    latency = dict()
    stack = list()
    visited = list()
    stack.append(node)
    visited.append(node)
    latency[node] = 0
    while len(stack) > 0:
        ele = stack.pop()
        try:
            for _tmp in ckt_dict[ele][1]:
                if _tmp in visited:
                    continue
                stack.append(_tmp)
                visited.append(_tmp)
                if ckt_dict[ele][0] == "DFF":
                    if _tmp in latency.keys():
                        latency[_tmp] = max(latency[_tmp], latency[ele] + 1)
                    else:
                        latency[_tmp] = latency[ele] + 1
                else:
                    if _tmp in latency.keys():
                        latency[_tmp] = max(latency[_tmp], latency[ele])
                    else:
                        latency[_tmp] = latency[ele]
        except:
            pass
    
    for _in in [i for i in pi if i.startswith('in')]:
        try:
            final_latency = max(final_latency, latency[_in])
            #print(_in, latency[_in])
        except:
            pass
    #print(latency)
    return final_latency
"""