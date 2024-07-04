def read_file(filepath):
    with open(filepath, "r") as fileOUT:
        lines = fileOUT.readlines()
    return lines

def tab_nodes(words,step_n,values):

    if words[:2] == ['Elmnr', 'Nodnr']:
        variables = words[2:]
        length = len(words)
        values = True

    if words[0] == 'Output':
        values = False

    if values:
        record = {'Step': step_n}

        if len(words) == length:
            elmn_n, nodn_n = map(int, words[:2])
            record['Elmnr'] = elmn_n
            record['Nodnr'] = nodn_n

            for i, var in enumerate(variables):
                record[var] = float(words[2 + i])

        elif len(words) == length - 1:
            nodn_n = int(words[0])
            record['Elmnr'] = elmn_n
            record['Nodnr'] = nodn_n

            for i, var in enumerate(variables):
                record[var] = float(words[1 + i])

        data_list.append(record)
        
    return data_list, values

# def tab_ips(words,step_n,values):

#     if words[:2] == ['Elmnr', 'Intpt']:
#         variables = words[2:]
#         length = len(words)
#         values = True
#         continue

#     if words[0] == 'Output':
#         values = False
#         continue

#     if values:
#         current_elmnr = None

#         if all(element.isdigit() for element in values[:2]):
#             # If the first value is a digit, it is Elmnr
#             current_elmnr = int(words[0])
#             intpt = int(words[1])
#             rest_values = words[2:]
#         else:
#             # Otherwise, Elmnr is the current_elmnr and the first value is Intpt
#             intpt = int(words[0])
#             rest_values = words[1:]

#         # Convert the remaining values to floats or NaN if they are empty
#         float_values = [float(v) if v else np.nan for v in rest_values]

#         # Ensure the float_values list has the right length by filling missing values with NaN
#         while len(float_values) < 9:
#             float_values.append(np.nan)

#         # Create a record with the current Elmnr, Intpt, and the rest of the values
#         record = [current_elmnr, intpt] + float_values[:9]  # Ensure only 9 additional values are taken



#     if values:
#         record = {'Step': step_n}

#         if len(words) == length:
#             elmn_n, intpt = map(int, words[:2])
#             record['Elmnr'] = elmn_n
#             record['Intpt'] = intpt

#             for i, var in enumerate(variables):
#                 record[var] = float(words[2 + i])

#         data_list.append(record)

#     return data_list, values

def process_tabulated_analysis(file_path):
    data_list = []
    variables = []
    length = 0

    step_n = None
    nodes = None
    intpnt = None
    values = False
    
    lines = read_file(file_path)

    for line in lines[1:]:
        Nodes = False
        Intpnt = False
        words = line.split()

        if not words:
            continue

        if words[:2] == ['Step', 'nr.']:
            step_n = words[2]
            continue
        
        if words[0] == 'Output':
            values = False
        if words[1] == 'NODES':
            Nodes = True
            Intpnt = False

        if nodes:    
            data_list_nodes, values = tab_nodes(words,step_n, values) #Processing  

        if words[1] == 'INTPNT':
            Nodes = False
            Intpnt = True
        if intpnt:
            words = re.split(r'\s+', line.strip())
            data_list_intpnt, values = tab_intpnt(words,step_n, values)
        
    return data_list_nodes, data_list_intpnt

