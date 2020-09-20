
import pandas as pd 
import os 
import glob 
import sys 
import re
from generate_lexi import load_annotations
from nltk.tokenize import word_tokenize
#need to remove double spaces 
def pre_process_text(s:str): 
    s = word_tokenize(s.lower())
    s = " ".join(s).replace(" .",".")
    return  s
def search_symptoms(symp_dict,sentence):
    found = False 
    matches = list() 
    for k in symp_dict: 
        searcher = list(re.finditer(f'(\b|\W)({k})(\b|\W)',sentence)) 
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
def gen_negation_range(neg_match,symp_dict): 
    """ Each match will have a group sturcture (word)(punctuation|space)(word)(punctuation|space) 
    The words to be negated are whatever is to the left of the punctuation if there is any. 
    Therefore for each negation match see if there's a punctuation mark and prune it. 
    Return only the tuple representing the  terms to be considered for negation 
        if there is a symptom to be removed it will be in this  tuple . 
    """ 
    out = list()  
    for e in neg_match: 
        groups:tuple = e.groups()  
        if None in groups:
            print(groups)
            idx = groups.index(None)
            groups = groups[0:idx]
        dummy:str = "".join(groups)
        dummy = re.sub('([\.\;\:\(\)].*)',"",dummy).strip()
        if dummy in symp_dict:
            continue
        #basically i made it so that a regex removes any trailing punctuaiton 
        out.append(dummy.split(" "))
    return out 

def add_note(symp_dict,symp_matches,text,negation_ranges): 
    negs = list()
    cuis = list() 
    for e in symp_matches: 
        term:str= e.groups()[1]
        moded = False  
        cuis.append(symp_dict[term])
        for k in negation_ranges: 
            if term in k: 
                negs.append("1")
                moded = True 
                break 
        if not moded: 
            negs.append("0")
    return ("$$$".join(cuis), "$$$".join(negs))
def annotate_individual(sample:pd.Series,symp_dict,negations):
    ID = sample['ID']
    txt = pre_process_text(sample['TEXT'])
    o1 = search_symptoms(symp_dict,txt)
    o2 =search_negation(negations,txt)
    if ID =="hsqxyq":
        breakpoint()
    neg_range = gen_negation_range(o2,symp_dict)
    (cuis, negations)= add_note(symp_dict,o1,txt,neg_range)
    sample['Symptom CUIs'] = f"$$${cuis}$$$"
    sample['Negation Flag'] = f"$$${negations}$$$"
    return sample[['ID','TEXT','Symptom CUIs','Negation Flag']]


def build_symps():
    lexicon :pd.DataFrame= pd.read_csv('COVID-Twitter-Symptom-Lexicon.txt',sep='\t',names=['gen','code','desc'])
    symp_dict = {} 
    code_2_gen= {}
    for _,e in lexicon.iterrows():
        (term_id,words) = (e['code'],e['desc'])
        gen = e['gen']
        symp_dict[words] = term_id
        code_2_gen[term_id] = gen 
    additional:dict = load_annotations() 
    for k in additional: 
        if k not in symp_dict.keys():
            symp_dict[k]= additional[k]
            #print(f"Adding {k} with {additional[k]} which should be {code_2_gen[additional[k]]}")
    return (symp_dict,code_2_gen)
def build_negations(): 
    rem_regex = r'(\s?\W\s?)?(\w*\b)?(\s?\W\s?)?(\w*\b)?(\s?\W\s?)?(\w*\b)?' #this is the regex that matches the foward parts 
    #rem_regex = r'(\.\s|\s\)?(\w*\b)?(\.\s|\s)?(\w*\b)?(\.\s|\s)?(\w*\b)?' #this is the regex that matches the foward parts 
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
        if pd.isnull(row['TEXT']):
            continue
        processed.append( annotate_individual(row,symps,negs ) )
    final = pd.concat(processed,axis=1).T
    final.to_excel('final.xlsx')