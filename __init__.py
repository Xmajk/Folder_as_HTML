from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import session,request,abort,Response,make_response
from flask import send_file
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from folder_scrapper import Folder_scrapper
from typing import Dict,List,Tuple,Union
import threading
import time
import io
import zipfile
import json
import platform
import sys

#zde začíná konfigura aplikace

konfig_dict:Dict[str,Union[str,int,bool]]={}

system = platform.system()
if system == 'Windows':
    print("Běžíš na operačním systému Windows.")
    path_sep:str="\\"
elif system == 'Linux':
    print("Běžíš na operačním systému Linux.")
    path_sep:str="/"
else:
    print("Neznámý operační systém")
    sys.exit(0)
    
try:
    with open(f'konfiguration{path_sep}server.json',"r") as file:
        konfig_dict = json.loads(file.read())
except:
    input("Při otevírání souboru \"server.json\" nastala chyba")
    sys.exit(0)


semaphor:threading.Semaphore=threading.Semaphore(1)

app = Flask(__name__)

"""
V tomto příkladu je os.urandom(24) použito k vygenerování náhodného tajného klíče o délce 24 bytů.
Tímto způsobem získáte silný tajný klíč pro zabezpečení vaší aplikace.
"""
app.secret_key = os.urandom(24)  # Tajný klíč pro session

limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="memory://"
)

content_root:str=konfig_dict["content_root"]

folder_scrapper:Folder_scrapper=Folder_scrapper(content_root,path_sep)

content_folder:Dict[str,dict]=folder_scrapper.run_scrapping()

#zde končí konfigurace aplikace

def scrapper_thread():
    """metoda, která se spustí do threadu, aby aktualizovala obsah \"content\" složku"""
    while True:
        tmp=folder_scrapper.run_scrapping()
        with semaphor:
            global content_folder
            content_folder=tmp
        time.sleep(5)

update_thread=threading.Thread(target=scrapper_thread,args=())#vytvoření threadu pro aktualizaci obsahu složky
update_thread.start()#spuštění vlákna

def make_elements(content_folder:Dict[str,dict],path:str="")->Tuple[bool,str]:
    tmp:List[Tuple[bool,str]]=[]
    for key in content_folder.keys():
        if path=="":
            tmp.append((type(content_folder[key])==dict,key,key))
        else:
            tmp.append((type(content_folder[key])==dict,key,path+"/"+key))
    tmp = sorted(tmp, key=lambda x: not x[0])  # Seřadit podle hodnoty typu bool (první prvek tuple)
    return tmp

def do_compress_and_download(path:str) -> Response:
    """
    Funkce vracící HTTP odpověd, která stáhne uživateli zkompresovanou složku
    
    Parametry
    ---------
    path : str
        Cesta k složce
        
    Returns
    -------
    Response
        HTTP odpověd, která stáhne uživateli zazipovanou složku

    """
    folder_path = path  # Zadejte cestu ke složce, kterou chcete zkomprimovat
    folder_name:str=path.split(path_sep)[-1]
    # Vytvoření dočasného paměťového objektu pro ukládání komprimovaných dat
    memory_file = io.BytesIO()

    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))

    memory_file.seek(0)  # Přesun na začátek souboru

    # Vytvoření odpovědi Flask
    response = make_response(memory_file.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={folder_name}.zip'.encode('utf-8')
    response.headers['Content-Type'] = 'application/zip'
    response.headers['Content-Length'] = str(memory_file.getvalue().__len__())

    return response

@app.route("/")
def index():
    if 'prihlasen' in session and session['prihlasen']:
        jmeno = session['jmeno']
        return render_template('index.html', jmeno=jmeno),200
    else:
        return redirect(url_for('prihlasit'))
 
@app.route("/zapisky",methods=["GET"])    
def zapisky_root():
    return render_template("notes.html",
                           elements=make_elements(content_folder)
                           ),200

@app.route("/zapisky/<path:subpath>",methods=["GET"]) 
def zapisky_branch(subpath:str):
    elements:Dict[str,dict]={}
    for path_slice in subpath.split("/"):
        elements=content_folder.get(path_slice,None)
        if elements==None:
            abort(404)
    return render_template("notes.html",
                           elements=make_elements(elements,subpath)
                           ),200
    
@app.route("/zapisky/<path:subpath>/download",methods=["GET"]) 
def download(subpath:str):
    elements:Dict[str,dict]=content_folder
    for path_slice in subpath.split("/"):
        elements=elements.get(path_slice,None)
        if elements is None:
            abort(404)
    if type(elements)==str:
        path:str=f'{content_root}{path_sep}{path_sep.join(subpath.split("/"))}'
        return send_file(path, as_attachment=True)
    else:
        path:str=f'{content_root}{path_sep}{path_sep.join(subpath.split("/"))}'
        return do_compress_and_download(path)
    
@app.errorhandler(429)
def to_many_requests(error):
    return render_template("chyby/to_many_requests.html"),429

@app.errorhandler(404)
def to_many_requests(error):
    return render_template("chyby/page_not_found.html",url=request.full_path),404

app.run(host=konfig_dict["ip_address"],port=konfig_dict["port"],debug=konfig_dict["debug"])