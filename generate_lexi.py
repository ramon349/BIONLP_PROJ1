import pandas as pd 

def merge_symp_cui(exps,cuis,master_dict):
    e_list = exps.split('$$$')[1:-1]
    c_list = cuis.split('$$$')[1:-1]
    feat_dict ={a:b for (a,b) in zip( e_list,c_list)}
    for k in feat_dict: 
        if k not in master_dict: 
            master_dict[k] =  feat_dict[k]


def load_annotations():
    data = pd.read_excel('corea_ramon_annotation_file.xlsx')
    master_dict = {} 
    for i,e in data.iterrows():
        merge_symp_cui(e['Symptom Expressions'].lower(),e['Symptom CUIs'].upper(),master_dict)
    return master_dict


if __name__=="__main__":
    load_annotations()