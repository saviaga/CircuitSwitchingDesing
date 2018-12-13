# Quine McCluskey Method


def mul(x,y):
    """
    Multiplies 2 minterms
    :param x: minterm 1
    :param y: minterm 2
    :return: multiplied minterm
    """
    res = []
    for i in x:
        if i+"'" in y or (len(i)==2 and i[0] in y):
            return []
        else:
            res.append(i)
    for i in y:
        if i not in res:
            res.append(i)
    return res


def multiply(x,y):
    """
     # Multiplies 2 expressions

    :param x: exp 1
    :param y: exp 2
    :return: multiplied expression
    """
    res = []
    for i in x:
        for j in y:
            tmp = mul(i,j)
            res.append(tmp) if len(tmp) != 0 else None

    return res

def refine(my_list,dc_list):
    '''
    Removes don't care terms from a given list and returns the list
    :param my_list: List
    :param dc_list: don't cares
    :return: list without don't cares
    '''
    res = []
    for i in my_list:
        if int(i) not in dc_list:
            res.append(i)
    return res

def ConvertToVariable(x):
    '''
    Converts minterms to varialbes
    :param x: minterms
    :return: minterm converted in variable: a,b,c,etc
    '''
    var_list = []
    for i in range(len(x)):
        if x[i] == '0':
            var_list.append(chr(i+97)+"'")
        elif x[i] == '1':
            var_list.append(chr(i+97))
    return var_list

def flatten(x):
    """
    # Flattens a dictionary
    :param x: list
    :return: flattened terms
    """

    flattened_items = []
    for i in x:
        flattened_items.extend(x[i])
    return flattened_items

def findminterms(a):
    '''
    Finds out which minterms are merged.
    :param a:  minterms
    :return: merged terms
    '''

    x=[]
    gaps = a.count('-')
    if gaps == 0:
        return [str(int(a,2))]

    for i in range(pow(2,gaps)):
        x.append(bin(i)[2:].zfill(gaps))
    temp = []

    for i in range(pow(2,gaps)):
        temp2,ind = a[:],-1
        for j in x[0]:
            if ind != -1:
                ind = ind+temp2[ind+1:].find('-')+1
            else:
                ind = temp2[ind+1:].find('-')
            temp2 = temp2[:ind]+j+temp2[ind+1:]
        temp.append(str(int(temp2,2)))
        x.pop(0)
    return temp

def compare(a,b):
    '''
    Checks if 2 minterms differ by 1 bit only
    :param a: minterm a
    :param b: minterm b
    :return: True,false, mismatch index
    '''

    mismatch_index=0
    c = 0
    for i in range(len(a)):
        if a[i] != b[i]:
            mismatch_index = i
            c += 1
            if c>1:
                return (False,None)
    return (True,mismatch_index)
   
def removeTerms(chart,terms):
    '''
    Removes minterms which are already covered from chart

    :param _chart: chart
    :param terms: Essential Prime Implicants
    :return: none
    '''
    #
    for i in terms:
        for j in findminterms(i):
            try:
                del chart[j]
            except KeyError:
                pass

def findEssentialPrimeImplicants(x):
    '''
    :param x: Dictionary representation of the Prime Implicant Charts
    :return: Essential prime implicants from prime implicants chart
    '''
    res = []
    for i in x:
        if len(x[i]) == 1:
            res.append(x[i][0]) if x[i][0] not in res else None
    return res

def GenerateGroups(minterms):
    '''
    Generates groups according to the number of 1s in each binary number

    :param minterms:  List of minterms elements
    :return: A group with keys according to the number of 1s
            i.e {0: ['0000'],
                1: ['0001', '0010'],
                2: ['0011', '0101'],
                3: ['0111', '1011'],
                4: ['1111']}
    '''
    groups = {}
    size = len(bin(minterms[-1])) - 2
    for minterm in minterms:

        try:
            groups[bin(minterm).count('1')].append(bin(minterm)[2:].zfill(size))
        except KeyError:
            groups[bin(minterm).count('1')] = [bin(minterm)[2:].zfill(size)]
    return groups

def PrintGroups(groups, primary):
    '''
    Prints the dictionary in a pretty form
    :param groups: Receive a dictionary
    :return: nothing
    '''

    print("\n\nGroup\tMinterms\t\t\tBinary\n%s"%('-'*40))
    for i in sorted(groups.keys()):
        printed_group_num = False
        for j in groups[i]:
            if primary: #if first group
                print("%5d" % i + "\t%-20d%s" % (int(j, 2), j)) if printed_group_num==False else print(" " +"\t\t%-20d%s"%(int(j,2),j))
                printed_group_num = True
            else:
                print("%5d" % i + "\t%-24s%s" % (','.join(findminterms(j)), j)) if printed_group_num == False else print(" " +"\t\t%-24s%s" % (','.join(findminterms(j)), j))
                printed_group_num = True
        print('-' * 40)


def PrintPrimeImplicantChart(mt,dc,all_pi):
    """

    :param mt: List of minterms elements
    :param dc: List of don't care elements
    :param all_pi: all prime implicants
    :return:
    """
    sz = len(str(mt[-1])) # The number of digits of the largest minterm
    chart = {}
    print('\n\n\nPrime Implicant Chart:\n\n    Minterms    |%s\n%s'%(' '.join((' '*(sz-len(str(i))))+str(i) for i in mt),'-'*(len(mt)*(sz+1)+16)))
    for i in all_pi:
        merged_minterms,y = findminterms(i),0
        print("%-16s|"%','.join(merged_minterms),end='')
        for j in refine(merged_minterms,dc):
            x = mt.index(int(j))*(sz+1) # The position where we should put 'X'
            print(' '*abs(x-y)+' '*(sz-1)+'X',end='')
            y = x+sz
            try:
                chart[j].append(i) if i not in chart[j] else None # Add minterm in chart
            except KeyError:
                chart[j] = [i]
        print('\n'+'-'*(len(mt)*(sz+1)+16))

    return chart

def PetrickSimplification(chart,EssentialPrimeImplicants):
    """

    :param chart: the prime implicants chart
    :return: the final solution
    """
    P = [[ConvertToVariable(j) for j in chart[i]] for i in chart]
    while len(P)>1: # Keep multiplying until we get the SOP form of P
        P[1] = multiply(P[0],P[1])
        P.pop(0)
    final_result = [min(P[0],key=len)] # Choosing the term with minimum variables from P
    final_result.extend(ConvertToVariable(i) for i in EssentialPrimeImplicants) # Adding the EPIs to final solution
    return final_result

def QuineMcCluskey(mt,dc):
    '''
     Quine-McCluskey Method

    :param mt: List of minterms elements
    :param dc: list of don't care elements
    :return: Simplified Function
    '''

    mt.sort()
    minterms = mt+dc
    minterms.sort()
    #We get the size of the biggest element in the ordered list -2 (i.e 15 -> 0b1111 = 4)

    groups,all_pi = {},set()
    groups = GenerateGroups(minterms)# Generate groups with 1 difference
    PrintGroups(groups,True) #Print the groups in a pretty format

    # Process for creating tables and finding prime implicants starts
    while True:
        tmp = groups.copy()

        groups,m,marked,should_stop = {},0,set(),True
        l = sorted(list(tmp.keys()))

        for i in range(len(l)-1):
            for j in tmp[l[i]]: # Iterates through current group elements
                for k in tmp[l[i+1]]: # Iterates through next group elements
                    res = compare(j,k) # Compare the minterms
                    if res[0]: # If the minterms differ by 1 bit only
                        try: # Put a '-' in the changing bit and add it to corresponding group
                            if j[:res[1]]+'-'+j[res[1]+1:] not in groups[m]:
                               groups[m].append(j[:res[1]] + '-' + j[res[1] + 1:])

                        except KeyError:
                            # If the group doesn't exist, create it, put a '-' in the changing bit and add the number
                            groups[m] = [j[:res[1]]+'-'+j[res[1]+1:]]
                        should_stop = False
                        marked.add(j) # Mark element j
                        marked.add(k) # Mark element k
            m += 1  #create another group (we have exausted combinations in the current next two adjacents)

        #We search for those unmarked
        local_unmarked = set(flatten(tmp)).difference(marked) # from the temp table we take out those marked

        all_pi = all_pi.union(local_unmarked) # Adding Prime Implicants (those unmarked) to global list
        print("Unmarked elements(Prime Implicants of this table):")
        print(None) if len(local_unmarked) == 0 else print(', '.join(local_unmarked))

        if should_stop: # If the minterms cannot be combined further
            print("\n\nAll Prime Implicants: ",None) if len(all_pi)==0 else  print("\n\nAll Prime Implicants: ",', '.join(all_pi))
            break

        PrintGroups(groups, False)

    chart= PrintPrimeImplicantChart(mt,dc,all_pi)

    EssentialPrimeImplicants = findEssentialPrimeImplicants(chart) # Find Essential Prime Implicants
  #  print("\nEssential Prime Implicants: "+', '.join(str(i) for i in EssentialPrimeImplicants))

    removeTerms(chart,EssentialPrimeImplicants) # Remove Essential Prime Implicants related columns from chart

    if(len(chart) == 0): # If no minterms remain after removing Essential Prime Implicants  related columns
        final_result = [ConvertToVariable(i) for i in EssentialPrimeImplicants] # Final result with only Essential Prime Implicants
    else: # Else follow Petrick's method for further simplification
        final_result = PetrickSimplification(chart,EssentialPrimeImplicants)

    return ('\n\nSolution: F = '+' + '.join(''.join(i) for i in final_result))


#**********************Quine-McCluskey Metod**********************************************

#Get the minterms and don't cares from user
#(comma (,) separated)
#minterms = [int(i) for i in input("Enter the minterms : ").strip().split()]
minterms = input("Enter values (comma (,) separated): ")
mintermsoneline = ([int(s) for s in minterms.split(',')])
#dontcares = [int(i) for i in input("Enter the don't cares. (Enter) if None : ").strip().split()]
dontcares = input("Enter the don't cares(comma (,) separated). (Enter) if None : ")
if dontcares:
        dontcaresoneline = ([int(s) for s in dontcares.split(',')])
else:
        dontcaresoneline=[]

print(QuineMcCluskey(mintermsoneline,dontcaresoneline)) 