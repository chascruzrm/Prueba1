import os, sys, string
from datetime import datetime
from os import environ, path

from constant import DUMPS_PATH, MAX_VARIABLE_NAME_LEN, SAVED_SESSIONS_PATH
from utils import print_err, print_warn
from help import help_str

class Persistence:
    
    def __init__(
      self, 
      variables: dict):
        self.variables = variables
        
        
    
    def save_vars(self, name: str, dest_dir = None):

        if not self.variables:
            print_err('No hay variables definidas.')
            return
        
        if not name:
            print_err('Debe ingresar un nombre para guardar.')
            return
        
        if not dest_dir: dest_dir = DUMPS_PATH

        name = name[:MAX_VARIABLE_NAME_LEN]

        try:
            os.makedirs(dest_dir, exist_ok=True)

            timestamp = datetime.now() \
                .isoformat(timespec='seconds') \
                .replace(':', '-')

            if path.exists(path.join(dest_dir, name)):
                os.rename(
                    path.join(dest_dir, name),
                    path.join(dest_dir, f'{name}-{timestamp}.bak'))
                print_warn(f'El nombre "{name}" ya existe. Se creó copia de respaldo.')

            with open(path.join(dest_dir, name), 'w+', encoding='utf-8') as f:
                for k in self.variables:
                    v = self.variables[k].replace('\n', '\\n').replace('\r', '')
                    f.write(f'{k[:MAX_VARIABLE_NAME_LEN]}={v}\n')

            print_warn('Variables guardadas.')

        except Exception as ex:
            import traceback; traceback.print_exc()


    def load_vars(self, name: str, from_dir = None):
        if not name:
            print_err('Debe ingresar un nombre para cargar.')
            return
        
        if not from_dir: from_dir = DUMPS_PATH
        
        name = name[:MAX_VARIABLE_NAME_LEN]
        
        try:
            os.makedirs(from_dir, exist_ok=True)

            if not path.exists(path.join(from_dir, name)):
                print_err(f'El nombre "{name}" no existe.')
                return

            with open(path.join(from_dir, name), 'r', encoding='utf-8') as f:
                while True:
                    l = f.readline()
                    if not l: break
                    l = l.strip('\r\n').replace('\\n', '\n')
                    parts = l.split('=', 1)
                    self.variables[ parts[0][:MAX_VARIABLE_NAME_LEN] ] = parts[1] if parts[1] != None else ''

            # Restauramos la ayuda
            self.variables['SYS_HELP'] = help_str
            self.variables['ggl'] = '! {BROWSER_PATH} http://www.google.com.ar/search?q='
            self.variables['wr'] = '! {BROWSER_PATH} https://www.wordreference.com/es/translation.asp?tranword='
            
            print('Variables cargadas.')

        except Exception as ex:
            import traceback; traceback.print_exc()


    def saved_vars(self):
        try:
            os.makedirs(DUMPS_PATH, exist_ok=True)

            files = [
                f for f in os.listdir(DUMPS_PATH) 
                    if path.isfile(path.join(DUMPS_PATH, f))
                    and f[-5:] == '.save'
            ]

            if not files:
                print('No hay archivos de variables guardados.')
                return
            
            for f in files:
                print('   ', f)

        except Exception as ex:
            import traceback; traceback.print_exc()


    def load_last_session_vars(self):
        name = 'last_session.save'
        if not path.exists(path.join(SAVED_SESSIONS_PATH, name)):
            print_warn('No se ha encontrado archvio de variables de la última sesión.')
            return
        self.load_vars(name, SAVED_SESSIONS_PATH)


    def save_last_session_vars(self):
        name = 'last_session.save'
        self.save_vars(name, SAVED_SESSIONS_PATH)
