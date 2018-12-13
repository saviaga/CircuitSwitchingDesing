#!/usr/bin/python
# -- encoding: utf-8 --

import collections
import math


TRACE = False


# Neighbors list
def neighbors(item):
    lista_neighbors = []
    bits_fixos = list_bits(item)
    for bit_fixo in bits_fixos:
        block = []
        for valor in item:
            n = []
            for bit in range(len(valor)):
                if bit == bit_fixo:
                    n.append(1 - valor[bit])
                else:
                    n.append(valor[bit])
            block.append(n)
        lista_neighbors.append(tuple(block))
    return lista_neighbors


# List of bits
def list_bits(itens):
    lista = []
    # For every bit
    for j in range(len(itens[0])):
        igual = True
        for k in range(len(itens) - 1):
            if itens[k][j] != itens[k + 1][j]:
                igual = False
                break
        if igual:
            lista.append(j)
    return lista



def IndextoVector(valor, bits):
    v = []
    for i in range(bits):
        v.append((valor >> i) & 1)
    return v



def VectortoIndex(vetor):
    v = 0
    for i in reversed(vetor):
        v = (v << 1) + i
    return v



def MinBits(valores, irrelevante, fixo=0):
    maxval = max(valores + irrelevante + [0]) + 1
    bits = int(math.ceil(math.log(maxval) / math.log(2)))
    if bits < 1: bits = 1
    if fixo:
        if fixo < bits:
            print(
                "invalid number of bits for '%d' variables" % (fixo, bits))
            return bits
        else:
            return fixo

    return bits


def createblock(vetor):
    function_t = dict()
    bits = list_bits(vetor)
    for i in bits:
        function_t[i] = vetor[0][i] == 1
    return function_t


def calculateWeight(testados, irrelevante, vetores):
    peso = 0
    for v in vetores:
        k = VectortoIndex(v)
        if not (k in testados.keys()) and not (k in irrelevante):
            peso = peso + 1
    return peso


def grouptogether(testados, table, irrelevante, vetores, identified=">"):
    otimo = False
    if TRACE: print(identified + "vectores", vetores)
    blocks = neighbors(vetores)
    maior_block = vetores
    peso = 0
    for block in blocks:
        if TRACE: print(identified + "testing neighbor", block)
        encontrado = True
        for v in block:
            indice = VectortoIndex(v)
            if not (indice in table or indice in irrelevante):
                if TRACE: print(identified + " failed")
                encontrado = False
                break;
        if encontrado:
            if TRACE: print(identified + " testing one level above")
            block_encontrado, otimo = grouptogether(testados, table, irrelevante, vetores + list(block), identified + ">")
            novo_peso = calculateWeight(testados, irrelevante, block_encontrado)
            if (len(block_encontrado) > len(maior_block) or (
                    len(block_encontrado) == len(maior_block) and novo_peso > peso)):
                if TRACE and peso > 0: print(
                    (identified + "best one found %d, (last was %d), substitute") % (
                    novo_peso, peso))
                maior_block = block_encontrado
                peso = novo_peso

            if (otimo):
                break;
            if (len(maior_block) == (1 << len(vetores[0]))):
                break;
        else:
            if (len(vetores) == (1 << (len(vetores[0]) - 1))):
                otimo = True

    if TRACE: print(identified + "best found", maior_block,
                    ", peso %d" % calculateWeight(testados, irrelevante, maior_block))
    return (maior_block, otimo)


def simplify(table, irrelevante, bits=0):
    numbits = MinBits(table, irrelevante, bits)
    testados = dict()
    final_groups = []
    function_t = []
    for i in table:

        if not i in testados.keys():

            if TRACE: print("Testing")
            g, _ = grouptogether(testados, table, irrelevante, [IndextoVector(i, numbits)])
            final_groups.append(g)
            function_t.append(createblock(g))
            for v in g:
                k = VectortoIndex(v)
                testados[k] = True
    return function_t, final_groups



def check(function_t, indice, bits):
    numbits = MinBits([indice], [], bits)
    v = IndextoVector(indice, numbits)
    valor = 0
    for block in function_t:
        valor_block = 1
        for i in reversed(list(block.keys())):
            if i >= numbits:
                valor_block = valor_block and (0 == block[i])
            else:
                valor_block = valor_block and (v[i] == block[i])
            if not valor_block:
                break
        valor = valor or valor_block
        if valor:
            break
    return valor


def validate(table, irrelevante, bits=0):
    numbits = MinBits(table, irrelevante, bits)
    f,final_groups = simplify(table, irrelevante, numbits)
    for i in range(1 << numbits):
        if not (i in irrelevante):
            v = check(f, i, numbits)
            if ((i in table and v != 1) or (not (i in table) and v == 1)):
                return []
    return f,final_groups


def reverseBits(v, bits):
    r = 0;
    for i in range(bits):
        r = r | (((v >> i) & 1) << (bits - i - 1))
   # print("reverseBits",r)
    return r


def FunctionInLetter(s, bits):
    import re
    s = s.upper()
    if re.search("[^A-Z +/.]", s):
        raise Exception("invalid")
    table = []
    bits = max(ord(max(s)) - ord('A') + 1, bits)
    variaveis = [chr(c + ord('A')) for c in range(bits)]
    for b in s.split("+"):
        r = 0;
        block = list(map(lambda x: str.strip(x, " ."), re.findall("(?: |[/.])?(?:[A-Z])", b.replace("//", ""))))
        utilizar_block = True
        for variavel in block:
            if len(variavel) == 2:
                continue
            idx = ord(variavel[0]) - ord('A')
            if "/" + variavel in block:
                utilizar_block = False
                break
            r = r | (1 << idx)
        if not utilizar_block:
            continue

        x = [r]
        for variavel in variaveis:
            if not variavel in b:
                i = len(x)
                for k in range(i):
                    idx = ord(variavel[0]) - ord('A')
                    x.append(x[k] | (1 << idx))
        table = list(set(table + x))
    return (table, bits)

def print_dic(dct):
    for item, amount in dct.items():
        print("{} --> {}".format(item, amount))

def atest(final_groupa):
    main_list = []
    for elem in final_groupa:
        list = []
        for i in elem:

            strngc = ''
            num = 0

            for c in i:
                strngc += str(c)
                num = (int(strngc, 2))

            list.append(num)
        main_list.append(list)

    list_numbers = []
    for elem in main_list:  # Converts list of list to just one list
        for i in elem:
            list_numbers.append((i))
    atestgroups = {}
    duplicates = ([item for item, count in collections.Counter(list_numbers).items() if
                   count > 1])  # gets the duplicates from the list
    for elem in main_list:  # create a new list of lists without duplicates
        atestgroups[str(elem)] = ([e for e in elem if e not in (duplicates)])
    return atestgroups

def convert_list_to_nums(elem):
    lista = []
    for i in elem:  # recorre elementos sublista
        strngc = ''
        num = 0

        for c in i:  # por cada elemento en la sublista
            strngc += str(c)  # conviertelo en string
            num = (int(strngc, 2))  # conviertelo en numero

        lista.append(num)

    return lista

def get_same_lenght_elem(sublist,size):

    elem_same_lenght = [word for word in sublist if len(word) == size]
    return elem_same_lenght

def convert_to_list(listoflist):
    list_numbers = []
    for elem in listoflist: #Converts list of list to just one list
        for i in elem:
            list_numbers.append((i))
    return list_numbers


def btest(final_groupb):

    finalbtestbroups = []
    allbtestgroups = final_groupb.copy()
    allbtestgroups.sort(key=len)
    output=[]
    for elem in allbtestgroups:

        if (len(elem) == 1):
            if not elem in finalbtestbroups:
                finalbtestbroups.append(elem)
            set_of_specific_element = set(elem)
            output = [
                item
                for item in allbtestgroups
                if not set_of_specific_element.intersection(set(item))
            ]
            allbtestgroups = output
        else:
            same_lenght_elems = get_same_lenght_elem(allbtestgroups, len(elem))  # get list of elements with same lenght
            for selem in same_lenght_elems:  # check each sub elem in list
                dict_elem = {}
                for e in selem:
                    ex = {e}
                    dict_elem[e] = len([sublist for sublist in output if ex.intersection(sublist)])
                maxvalue = max(dict_elem, key=dict_elem.get)
                if not maxvalue in finalbtestbroups:
                    finalbtestbroups.append(maxvalue)
                set_of_specific_element = set(selem)
                allbtestgroups = [
                    item
                    for item in allbtestgroups
                    if not set_of_specific_element.intersection(set(item))
                ]  # eliminate those elements from the list of btestgroups so we can keep check without them

    print("\nfinal b test groups",finalbtestbroups)

    return finalbtestbroups

if __name__ == "__main__":
    import sys

    bits = 0
    table = []
    irrelevante = []
    usage = '''Sintaxe: %s [table [irrelevante [bits]] | --help ]
.''' % sys.argv[0]

    if len(sys.argv) == 2 and (sys.argv[1] == '-h' or sys.argv[1] == '--help'):
        print(usage)
    else:
        if (len(sys.argv) > 1):
            if len(sys.argv) > 3: bits = int(sys.argv[3])
            while (True):
                try:
                    table = sys.argv[1].split(",")
                    if len(table) == 1 and table[0].strip() == '':
                        table = []
                    else:
                        table = [int(x, 0) for x in table]
                except:
                    table, bits = FunctionInLetter(sys.argv[1], bits)

                if (len(sys.argv) > 2):
                    try:
                        ibits = bits
                        irrelevante = sys.argv[2].split(",")
                        if len(irrelevante) == 1 and irrelevante[0].strip() == '':
                            irrelevante = []
                        else:
                            irrelevante = [int(x, 0) for x in irrelevante]
                    except:
                        irrelevante, ibits = FunctionInLetter(sys.argv[2], bits)
                    if (bits == ibits):
                        break
                    else:
                        bits = max(ibits, bits)
                else:
                    break

        else:
            reverse = True
            if len(sys.argv) > 1 and sys.argv[1] == "A=lsb":
                reverse = False
            bits = int(input("Number of variables: "))

            if (bits < 1):

                print("Invalid")
                exit(1)
            for j in range(1 << bits):
                i = j
                if reverse:
                    i = reverseBits(j, bits)
                ok = False
                while (not ok):
                    ok = True
            oneline = input("Enter values: ")
            onelinenum = ([int(s) for s in oneline.split(',')])
            onelinenum = sorted(onelinenum)
            onelinenumreverse = ([reverseBits(s,bits) for s in onelinenum])
            table = onelinenumreverse.copy()
        bits = MinBits(table, irrelevante, bits)
        funcion_final,grupos_final=(validate(sorted(table), irrelevante, bits))
        print("\na-test:")
        print_dic(atest(grupos_final))  # Does the atest and prints it

        grupostbtest=[]
        vecinosb=[]
        list_numbers = []
        lista_numvecinos=[]
        number_listgrupofinal=[]
        btestgroups=[]
        for elem in grupos_final:  # recorre elements lista principal
            list = []
            for i in elem:  # recorre elementos sublista

                strngc = ''
                num = 0

                for c in i:  # por cada elemento en la sublista
                    strngc += str(c)  # conviertelo en string
                    num = (int(strngc, 2))  # conviertelo en numero

                list.append(num)
            number_listgrupofinal.append(list)
        gruposonelist = convert_to_list(number_listgrupofinal)
        print("\nb test")
        for elem in grupos_final:
            print(convert_list_to_nums(elem))
            vecinosb=neighbors(elem)
            listav = []
            for i in vecinosb:  # recorre elements lista principal
                    listav.append(convert_list_to_nums(i))
            for elem in listav:  # iterate over the vecinos list
                btestgroups.append([e for e in elem if e not in (gruposonelist)])
        btest(btestgroups)
