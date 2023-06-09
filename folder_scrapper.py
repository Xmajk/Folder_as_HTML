from typing import List,Dict,Union,Tuple
import os

class Folder_scrapper:

    def __init__(self,absolute_root_path:str,path_sep:str) -> None:
        self.__root_path:str=absolute_root_path
        self.__path_sep:str=path_sep
        
    def run_scrapping(self)->Dict[str,Union[str,dict]]:
        os.chdir(self.__root_path)
        output_dict:Dict[str,Union[str,dict]]={}
        for element in os.listdir():
            if os.path.isdir(element):
                output_dict[element]=self.__scrap_folder(f'{self.__root_path}{self.__path_sep}{element}')
                continue
            output_dict[element]=element
        return output_dict
    
    def __scrap_folder(self,path)->Dict[str,Union[str,dict]]:
        tmp:Dict={}
        for element in os.listdir(path):
            if os.path.isdir(f'{self.__root_path}{self.__path_sep}{element}'):
                tmp[element]=self.__scrap_folder(f'{self.__root_path}{self.__path_sep}{element}')
                continue
            tmp[element]=element
        return tmp
    
        