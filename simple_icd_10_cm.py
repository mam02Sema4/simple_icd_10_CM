import simple_icd_10 as icd

code_index_map = {} #contains the index of the codes in code_data_list for faster access

code_data_list = [] #contains all the icd-10-cm codes and their data

ancestors_dict = {}

descendants_dict = {}

use_memoization = True

def _load_codes():
    f = open("data/icd10cm-order-Jan-2021.txt", "r")
    i=0
    for line in f:
        fields=[line[6:13].strip(),line[14]=="1",line[77:].strip()] #saves the code, the boolean that tells if it's a leaf and the long description
        code_data_list.append(fields)
        code_index_map[fields[0]]=i #saves in the map the index of the code in code_data_list
        i=i+1

_load_codes()


def _remove_dot(code):
    if len(code)>4 and code[3]==".":
        code=code[:3]+code[4:]
    return code

def is_valid_item(code):
    return (_remove_dot(code) in code_index_map) or icd.is_chapter_or_block(code)

def is_category_or_subcategory(code):
    return _remove_dot(code) in code_index_map

def is_chapter_or_block(code):
    return icd.is_chapter_or_block(code)

def is_chapter(code):
    return icd.is_chapter(code)

def is_block(code):
    return icd.is_block(code)

def is_category(code):
    return (_remove_dot(code) in code_index_map) and (len(_remove_dot(code))==3)

def is_subcategory(code):
    return (_remove_dot(code) in code_index_map) and (len(_remove_dot(code))>3)

def get_description(code):
    if is_category_or_subcategory(code):
        return code_data_list[code_index_map[_remove_dot(code)]][2]
    elif is_chapter_or_block(code):
        return icd.get_description(code)
    else:
        raise ValueError(code+" is not a valid ICD-10-CM code.")

def is_leaf(code):
    if is_category_or_subcategory(code):
        return code_data_list[code_index_map[_remove_dot(code)]][1]
    elif is_chapter_or_block(code):
        return False
    else:
        raise ValueError(code+" is not a valid ICD-10-CM code.")
    
'''
def get_all_codes(keep_dots):
    if keep_dots:
        return all_codes.copy()
    else:
        return all_codes_no_dots.copy()

def get_index(code):
    c = _remove_dot(code)
    return _get_index(c)

#gets index without trying to remove the dot first
def _get_index(code):
    for i in range(len(all_codes_no_dots)):
        if all_codes_no_dots[i]==code:
            return i
    raise ValueError(code+" is not a valid ICD-10 code.")

def _get_chapter(code):
    if code in chapter_list:
        return code
    code = _remove_dot(code)
    l = code[0] #first letter of the code
    n = int(code[1:3]) #second and third digits of the code, as an integer
    if l=="A" or l=="B":
        return "I"
    elif l=="C" or (l=="D" and n<=48):
        return "II"
    elif l=="D":
        return "III"
    elif l=="E":
        return "IV"
    elif l=="F":
        return "V"
    elif l=="G":
        return "VI"
    elif l=="H" and n<=59:
        return "VII"
    elif l=="H":
        return "VIII"
    elif l=="I":
        return "IX"
    elif l=="J":
        return "X"
    elif l=="K":
        return "XI"
    elif l=="L":
        return "XII"
    elif l=="M":
        return "XIII"
    elif l=="N":
        return "XIV"
    elif l=="O":
        return "XV"
    elif l=="P":
        return "XVI"
    elif l=="Q":
        return "XVII"
    elif l=="R":
        return "XVIII"
    elif l=="S" or l=="T":
        return "XIX"
    elif l=="V" or l=="X" or l=="Y":
        return "XX"
    elif l=="Z":
        return "XXI"
    elif l=="U":
        return "XXII"

def get_descendants(code):
    if not is_valid_item(code):
        raise ValueError(code+" is not a valid ICD-10 code.")
    code = _remove_dot(code)
    if use_memoization:
        if code in descendants_dict:
            return descendants_dict[code].copy()
        else:
            descendants_dict[code] = _get_descendants(code)
            return descendants_dict[code].copy()
    else:
        return _get_descendants(code)

def _get_descendants(code):
    if code in chapter_list:#if it's a chapter
        return _select_adjacent_codes_with_condition(lambda c:_get_chapter(c)==code,_get_index(code))
    elif len(code)==7:#if it's a block
        #we consider first the three blocks whose codes don't all begin with the same letter
        if code=="V01-X59":
            return ["V01-V99", "W00-X59"] + get_descendants("V01-V99") + get_descendants("W00-X59")
        elif code=="W00-X59":
            t = ["W00-W19", "W20-W49", "W50-W64", "W65-W74", "W75-W84", "W85-W99", "X00-X09", "X10-X19", "X20-X29", "X30-X39", "X40-X49", "X50-X57", "X58-X59"]
            return t + [c for l in [get_descendants(x) for x in t] for c in l]
        elif code=="X85-Y09":#this is simpler since all its children are codes
            return _select_adjacent_codes_with_condition(lambda c:not is_chapter_or_block(c) and ((c[0]=="X" and int(code[1:3])>=85) or (c[0]=="Y" and int(code[1:3])<=9)),_get_index(code))
        else:
            #the first part of the lambda expression checks for categories, the second checks for blocks
            return _select_adjacent_codes_with_condition(lambda c:(not is_chapter_or_block(c) and c[0]==code[0] and int(c[1:3])>=int(code[1:3]) and int(c[1:3])<=int(code[-2:]))or(is_chapter_or_block(c) and not c in chapter_list and c[0]==code[0] and int(c[1:3])>=int(code[1:3]) and int(c[-2:])<=int(code[-2:]) and not c==code),_get_index(code))
    elif len(code)==3:#if its a category
        return _select_adjacent_codes_with_condition(lambda c:c[:3]==code and not c==code and len(c)<7,_get_index(code))
    else:#if its a subcategory
        if code=="B180":#two special cases
            return ["B1800", "B1809"]
        elif code=="B181":
            return ["B1810", "B1819"]
        else:
            return []#it has not children

def get_ancestors(code):
    if not is_valid_item(code):
        raise ValueError(code+" is not a valid ICD-10 code.")
    code = _remove_dot(code)
    if use_memoization:
        if code in ancestors_dict:
            return ancestors_dict[code].copy()
        else:
            ancestors_dict[code] = _get_ancestors(code)
            return ancestors_dict[code].copy()
    else:
        return _get_ancestors(code)

def _get_ancestors(code):
    if code in chapter_list:#if its a chapter
        return []#it has no parent
    elif is_chapter_or_block(code):#if its a block
        i = _get_index(code)
        if code=="V01-V99" or code=="W00-X59":#we start with the special cases
            return ["V01-X59"] + get_ancestors("V01-X59")
        elif code=="W00-W19" or code=="W20-W49" or code=="W50-W64" or code=="W65-W74" or code=="W75-W84" or code=="W85-W99" or code=="X00-X09" or code=="X10-X19" or code=="X20-X29" or code=="X30-X39" or code=="X40-X49" or code=="X50-X57" or code=="X58-X59":
            return ["W00-X59"] + get_ancestors("W00-X59")
        else:
            for h in range(1,i+1):
                k=i-h
                if(len(all_codes_no_dots[k])==7 and code[0]==all_codes_no_dots[k][0] and code in get_descendants(all_codes_no_dots[k])):
                    return [all_codes_no_dots[k]] + get_ancestors(all_codes_no_dots[k])
            return [_get_chapter(code)]
    elif len(code)==3:#if its a category
        i = _get_index(code)
        for h in range(1,i+1):
            k=i-h
            if len(all_codes_no_dots[k])==7:#the first category we meet going to the left will contain our code
                return [all_codes_no_dots[k]] + get_ancestors(all_codes_no_dots[k])
    else:#if its a subcategory
        return [code[:-1]] + get_ancestors(code[:-1])

def is_ancestor(a,b):
    if not is_valid_item(a):
        raise ValueError(a+" is not a valid ICD-10 code.")
    return a in get_ancestors(b)

def is_descendant(a,b):
    return is_ancestor(b,a)

def get_nearest_common_ancestor(a,b):
    anc_a = [a] + get_ancestors(a)
    anc_b = [b] + get_ancestors(b)
    if len(anc_b) > len(anc_a):
        temp = anc_a
        anc_a = anc_b
        anc_b = temp
    for anc in anc_a:
        if anc in anc_b:
            return anc
    return ""

def reset_memoization():
    global ancestors_dict
    ancestors_dict = {}
    global descendants_dict
    descendants_dict = {}

def enable_memoization():
    global use_memoization
    use_memoization = True

def disable_memoization():
    global use_memoization
    reset_memoization()
    use_memoization = False

#returns all the codes that respect the condition in "condition", supposing that all these codes are adjacent in all_codes_no_dots, starting from the ith code
def _select_adjacent_codes_with_condition(condition, i=0):
    while(i<len(all_codes_no_dots) and not condition(all_codes_no_dots[i])):
        i = i+1
    l = []
    while(i<len(all_codes_no_dots) and condition(all_codes_no_dots[i])):
        l.append(all_codes_no_dots[i])
        i = i+1
    return l
    
    
'''