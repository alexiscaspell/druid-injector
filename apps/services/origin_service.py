from apps.models.origin import DataOrigin
from typing import List,Dict
import csv
import locale
import json


FILE_ENCODING=locale.getpreferredencoding()

def get_info(origin:DataOrigin)->List[Dict]:
    method_to_call = f'get_info_from_{origin.type.value}'
    return globals()[method_to_call](origin.metadata)

def get_info_from_csv(data:Dict)->List[Dict]:
    result=[]
    path=data["path"]
    with open(path,newline='\n',encoding=FILE_ENCODING) as MyFile:
        myfile = csv.reader(MyFile)         
        first_line = True

        for line in myfile:
            d = {}
            if first_line:
                headers = line
                first_line=False
                continue
            for i, header in enumerate(headers):
                d.update({header: line[i]})

            result.append(d)
                        
    return result

def get_info_from_json(data:Dict)->List[Dict]:
    with open(data["path"]) as file:
        return json.load(file)
