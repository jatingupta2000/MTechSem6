from operation import *

# Generate Data Files
#dump_initial_data_file('large.bench')

# Load Circuit Analysis
ckt, dff_input, dff_output, dff_io_map, pi, po, ckt_dict, logic_cone, key_in_logic_cone = load_intial_data()

print(key_in_logic_cone[dff_io_map['o1']])
