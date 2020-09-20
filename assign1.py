
import pandas as pd 
import os 
import glob 
import sys 
import re



def search_symptoms(symp_dict,sentence):
    found = False 
    matches = list() 
    for k in symp_dict: 
        searcher = list(re.finditer(f'({k})',sentence)) 
        if searcher: 
            matches.extend(searcher)  
            found = True 
    return matches
def search_negation(negations,sentence):
    """  
    There may be multiple negations in the same sentence. hence we use search iter. 
    once the list of matches is found. We simply flatten it onto a single match list  
    """ 
    found = False 
    matches = list() 
    for e in negations: 
        searcher = list(re.finditer(e,sentence))
        if searcher:
            matches.extend(searcher)
            found = True 
    return matches
def gen_negation_range(neg_match): 
    """ Each match will have a group sturcture (word)(punctuation|space)(word)(punctuation|space) 
    The words to be negated are whatever is to the left of the punctuation if there is any. 
    Therefore for each negation match see if there's a punctuation mark and prune it. 
    Return only the tuple representing the  terms to be considered for negation 
        if there is a symptom to be removed it will be in this  tuple . 
    """ 
    out = list()  
    for e in neg_match: 
        groups = e.groups() 
        try: 
            idx = groups.index('.')
            out.append(groups[0:idx])
        except ValueError: 
            out.append(groups)
    return out 

def add_note(symp_dict,symp_matches,text,negation_ranges,code_2_gen): 
    terms = list() 
    negs = list()
    cuis = list() 
    gen_symps = list()
    for e in symp_matches: 
        term = e.groups(1)[0] 
        moded = False  
        terms.append(term)
        cuis.append(symp_dict[term])
        gen_symps.append(code_2_gen[symp_dict[term]])
        for k in negation_ranges: 
            if term in k: 
                negs.append("1")
                moded = True 
                break 
        if not moded: 
            negs.append("0")
    return ("$$$".join(terms),"$$$".join(gen_symps),"$$$".join(cuis), "$$$".join(negs))
def annotate_individual(sample:pd.Series,symp_dict,negations,code_2_gen):
    ID = sample['ID']
    txt = sample['TEXT']
    o1 = search_symptoms(symp_dict,txt)
    o2 =search_negation(negations,txt)
    neg_range = gen_negation_range(o2)
    (matched,generic, cuis, negations)= add_note(symp_dict,o1,txt,neg_range,code_2_gen)
    sample['Symptom Expressions'] = matched 
    sample['Standard Symptom'] = generic 
    sample['Symptom CUIS'] = cuis 
    sample['Negation Flag'] = negations 
    return sample


def build_symps():
    lexicon :pd.DataFrame= pd.read_csv('COVID-Twitter-Symptom-Lexicon.txt',sep='\t',names=['gen','code','desc'])
    symp_dict = {} 
    code_2_gen= {}
    for _,e in lexicon.iterrows():
        (term_id,words) = (e['code'],e['desc'])
        gen = e['gen']
        symp_dict[words] = term_id
        code_2_gen[term_id] = gen
    return (symp_dict,code_2_gen)
def build_negations(): 
    rem_regex = r'(\.\s|\s)?(\w*\b)?(\.\s|\s)?(\w*\b)?(\.\s|\s)?(\w*\b)?' #this is the regex that matches the foward parts 
    neg_text = [ r"(\b{}\b){}".format(e,rem_regex) for e in open('./neg_trigs.txt').read().split('\n') ]
    return neg_text
def main(): 
    pass 
if __name__=="__main__":
    negs = build_negations()
    symps,code_2_gen = build_symps()
    input_file = sys.argv[1]
    reddit = pd.read_excel(input_file)
    processed = list()
    for index,row in reddit.iterrows() : 
        processed.append (annotate_individual(row,symps,negs,code_2_gen) )
    final = pd.concat(processed,axis=1).T
    final.to_excel('pokemon_test.xlsx')