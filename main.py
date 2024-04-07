
from colorama import Fore, Back, Style, init
from commands import misc_commands
from commands.vars_commands import VarsCommands
from constant import MAX_VARIABLE_NAME_LEN, PROMPT
from help import help_str
from util_persistence import Persistence
from utils import is_valid_identifier, print_err, print_warn, slugify
from utils_openai import OpenAIWrapper


# Preemptively load the readline module so that the 
# input() function has editing capabilities.
try:
    import readline
except:
    print('Python readline module no encontrado.')


class GPTArkan:
    
    "gpt-4-0125-preview"
    "gpt-3.5-turbo"
    CURRENT_AI_MODEL = 'gpt-4-0125-preview'

    # Here we set user's variables
    variables = {}

    # ChatGPT role
    variables['CHATGPT_ROLE'] = ''
    variables['SYS_HELP'] = help_str
    variables['BROWSER_PATH'] = '"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"'

    only_chatgpt_mode = False

    # Exit flag
    Salir = False
    
    
    def start(self):
        # Initialize colorama
        init()
        
        self.per = Persistence(self.variables)
        
        try:
            self.per.load_last_session_vars()
        except Exception as ex:
            import traceback; traceback.print_exc()

        self.oai = OpenAIWrapper(
            self.variables, 
            self.CURRENT_AI_MODEL)
        
        
        self.vars_comm_handlers = VarsCommands(
            self.variables
        )

        while not self.Salir:
            try:
                self._main()
            except Exception as ex:
                import traceback; traceback.print_exc()
            finally:
                self.per.save_last_session_vars()


    def _main(self):
        
        prefix = ''
        
        while True:
            print(Fore.LIGHTYELLOW_EX + PROMPT, end='')
            q = input(Fore.LIGHTGREEN_EX + ' ')
            print(Style.RESET_ALL + '', end='')

            if not q.strip():
                print('Escriba sin comillas "help" para ayuda, o presione "S" y luego ENTER para salir.\n')
                continue

            # Pongo este if antes de que se altere q
            if self.only_chatgpt_mode and q == '!normalmode':
                self.only_chatgpt_mode = False
                print_warn('Cambiado a modo de uso normal.')
                continue
            
            q = misc_commands.preprocess_chatgpt_mode(self, q)
            
            if q == '!chatgptmode':
                misc_commands.set_chatgpt_mode(self)
                continue

            if q.startswith('pre '):
                prefix = q[4:]
                continue

            if prefix:
                if not self.only_chatgpt_mode:
                    q = prefix + q
                
                    
            # Interpretar una varaible
            # Modifica a q, por eso pongo antes de que se 
            # expandan variables
            if q.startswith(':'):
                q2 = self.vars_comm_handlers.run_variable_content(q)
                if q2 == None:
                    continue
                q = q2
                

            # Expandir variables
            try:
                q = self.vars_comm_handlers.expand_query(q)
            except ValueError as ex1:
                print_err(ex1)
                continue
            except Exception as ex:
                import traceback; traceback.print_exc()
                continue


            if q in ('help', 'ayuda') or q in ('?help', '?ayuda'):
                print(help_str)
                continue


            # Multiline input
            if q.startswith('mli '):
                misc_commands.multi_line_input(self, q)
                continue
            
                    
            # Establecer rol de chatgpt
            if q.startswith('srol'):
                misc_commands.set_gpt_role(self, q)
                continue


            # Ejecutar comando de shell
            if q.startswith('! '):
                misc_commands.execute_shell_command(self, q)
                continue
            

            # Delimitador 1
            if q.startswith('d1 '):
                delim1 = q[3:]
                if not delim1: self.vars_comm_handlers.delim1 = '{'
                continue

            
            # Delimitador 2
            if q.startswith('d2 '):
                delim2 = q[3:]
                if not delim2: self.vars_comm_handlers.delim2 = '}'
                continue

            
            # Listar variables
            if q in ('v', 'vars') or q.startswith('v ') or q.startswith('vars '):
                self.vars_comm_handlers.list_vars(q)
                continue
            
            
            # Buscar dentro de variables
            if q.startswith('findv '):
                self.vars_comm_handlers.list_vars_by_value(q)
                continue
            
            
            # Imprime en pantalla una varaible
            if q.startswith('p '):
                self.vars_comm_handlers.print_var(q)
                continue

            
            # Copiar una variable a otra
            if q.startswith('cp '):
                self.vars_comm_handlers.copy_var(q)
                continue
            
            
            # Renombrar una variable
            if q.startswith('ren '):
                self.vars_comm_handlers.rename_var(q)
                continue


            # Borrar una variable
            if q.startswith('del '):
                self.vars_comm_handlers.del_var(q)
                continue
            

            # Borrar todas las self.variables
            if q == 'clearvars':
                self.variables.clear()
                continue
            
            
            # guardar las self.variables a un archivo
            if q.startswith('savevars '):
                name = slugify(q[9:])[:MAX_VARIABLE_NAME_LEN] + '.save'
                self.per.save_vars(name)
                continue
                

            # cargar self.variables desde un archivo
            if q.startswith('loadvars '):
                name = slugify(q[9:])[:MAX_VARIABLE_NAME_LEN] + '.save'
                self.per.load_vars(name)
                continue
                

            # Lista self.variables guardadas en archivos
            if q == 'savedvars':
                self.per.saved_vars()
                continue


            # Setea modelo de chatgpt
            if q.startswith('setmodel '):
                name = q[9:109].strip()
                if not name:
                    print_warn('Modelo actual: ' + self.oai.CURRENT_AI_MODEL)
                    print_warn('Ejemplos de modelos: gpt-4-0125-preview, gpt-3.5-turbo')
                    continue
                self.CURRENT_AI_MODEL = name
                self.oai.CURRENT_AI_MODEL = name
                continue


            # Sale del sistema
            if q.upper() in ('S', 'SALIR', 'EXIT', '?!S', '?!SALIR', '?!EXIT'):
                print('Hasta luego.\n')
                self.Salir = True
                return
            
            
            # Consulta a chatgpt
            if q.startswith('?'):
                self.variables['lastq'] = q[1:]
                print_warn('Esperando respuesta de ChatGPT...')
                r = self.oai.query_gpt(q[1:])
                self.variables['lastr'] = r
                print(r)
                continue

            
            # Asignar un valor a una variable
            if q.find('=') in range(0, MAX_VARIABLE_NAME_LEN + 1):
                parts = q.split('=', 1)
                name = parts[0].strip()[:MAX_VARIABLE_NAME_LEN]
                if is_valid_identifier(name):
                    self.variables[name] = parts[1] if parts[1] != None else ''
                    continue
            
            
            print_err(f'Comando incompleto o no reconocido: "{q}"')
            continue
        
        
if __name__ == '__main__':

    app = GPTArkan()
    app.start()
    