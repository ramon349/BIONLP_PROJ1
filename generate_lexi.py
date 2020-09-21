import pandas as pd 

# get the cuis and the symptoms add them to the master dict. 
def merge_symp_cui(exps,cuis,master_dict):
    exps = exps.lower()
    cuis = cuis.lower()
    e_list = exps.split('$$$')[1:-1]
    c_list = cuis.split('$$$')[1:-1]
    feat_dict ={a:b for (a,b) in zip( e_list,c_list)}
    for k in feat_dict: 
        master_dict[k] =  feat_dict[k]

#load the annotations i did and add them to the  symptom dict 
def load_annotations():
    data = pd.read_excel('correa_ramon_annotation_file.xlsx')
    master_dict = {} 
    for i,e in data.iterrows():
        merge_symp_cui(e['Symptom Expressions'].lower(),e['Symptom CUIs'].upper(),master_dict)
    return master_dict


if __name__=="__main__":
    load_annotations()