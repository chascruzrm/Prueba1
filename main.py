from datetime import datetime
import os, sys, string
from os import environ, path
from openai import OpenAI
from colorama import Fore, Back, Style, init
import subprocess

help_str = \
"""
COMANDOS
    - help o ayuda - Muestra esta ayuda.
    - s, salir o exit - Sale de la aplicación si se está en modo "normal".
    - !s, !salir o !exit - Sale de la aplicación si se está en modo "ChatGPT".

    - ? <prompt_chat_gpt> - Consulta a ChatGPT.
    
    - !chatgptmode - Activa modo exclusivo de conversación con ChatGPT.
    - !normalmode - Desactiva modo exclusivo de conversación con ChatGPT.
    
    - srol <rol_del_sistema> - Descripción del rol que desea para ChatGPT.
    - ! <comando_sistema> - Ejecuta una órden del shell.
    - pre <precondiciones> - Es un texto que se va a anteponer a lo que el usuario ingrese.
    - d1 <delimitador_inicial> - Establece el delimitador inicial de variables. Por defecto "{".
    - d2 <delimitador_final> - Establece el delimitador final de variables. Por defecto "}".
    - <nombre_varaible>=<valor> - Asigna un valor a una variable.
    - v o vars [<filtro_nombre_variable>] - Muestra todas (o las que cuyos nombren contengan
                                            lo especificado en el filtro) las variables 
                                            definidas y un vistazo de sus valores.
    - findv <filtro_contanido> - Lista un vistazo de las variables que contengan lo especificado
                                 en el filtro.
    - p <nombre_variable> - Muestra valor de variable.
    - cp <nombre_variable_origen> <nombre_variable_destino> - Copia una variable en otra.
    - ren <nombre_variable_origen> <nombre_variable_destino> - Renombra una variable.
    - del <nombre_variable> - Borra una variable.
    - :<nombre_variable> - Interpreta (ejecuta) lo que está dentro de la variable.
    - clearvars - Borra todas las variables definidas.
    - savevars <nombre_de_grupo_de_varaibles> - Guarda todas las variables a un archivo con el nombre del grupo en el disco.
    - loadvars <nombre_de_grupo_de_varaibles> - Carga todas las variables de un grupo, del disco a la memoria.
    - savedvars - Lista los nombres de grupos de varaibles guardados en el disco.

    - setmodel <nombre_modelo_gpt> - Indica a la app qué modelo de GPT usar.
      Por ejemplo (sin comillas): "setmodel gpt-4-0125-preview" o "setmodel gpt-3.5-turbo"
    
VARIABLES EN COMANDOS DE LA APP O EN PROMPTS ENVIADOS A CHATGPT
    - Si define una variable, por ej. con "!s var1=Marcelo" (sin comillas); podrá usarla en un 
      prompt escribiendo, por ejemplo (sin comillas): "?Cuál es el origen del nombre {var1}?". 
      De esta manera, esta app enviará a ChatGP el siguiente texto expandido (sin comillas): 
      "?Cuál es el origen del nombre Marcelo?"
      
    - La última consulta se almacena en la variable lastq.
    - La última respuesta de ChatGPT se guarda en la variable lastr.
    - La salida del último comando del sistema operativo otilizado se guarda en la variable lastcmd.
"""

# Preemptively load the readline module so that the 
# input() function has editing capabilities.
try:
    import readline
except:
    print('Python readline module no encontrado.')


"gpt-4-0125-preview"
"gpt-3.5-turbo"
CURRENT_AI_MODEL = 'gpt-4-0125-preview'

# Lista de conversación con ChatGPT
messages = []

# Here we set user's variables
variables = {}

# ChatGPT role
variables['CHATGPT_ROLE'] = ''
variables['SYS_HELP'] = help_str
variables['BROWSER_PATH'] = '"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"'

# Variable interpolation delimiters
# User can access its variables by referencing them in prompts
delim1 = '{'
delim2 = '}'
ESCAPE_CHAR = '\\'

# Largo máximo de nombres de variable de usuario
MAX_VARIABLE_NAME_LEN = 45
VARIABLE_CONTENT_PREVIEW = 60

# Script location
try:
    SCRIPT_DIR = path.dirname(path.realpath(__file__))
except Exception as ex:
    SCRIPT_DIR = sys.path[0]

# Place to put saved variables files
DUMPS_PATH = path.join(SCRIPT_DIR, 'var_dumps')
SAVED_SESSIONS_PATH = path.join(DUMPS_PATH, 'saved_sessions')

PROMPT = 'CHATGPT>'

only_chatgpt_mode = False

# Variables reservadas
# SYS_SHELL = 'cmd.exe'
# SYS_SHELL_PARAMS = '/c'

# Exit flag
Salir = False

# OpenAI Client
client = None

def load_apikey():
    with open(path.join(SCRIPT_DIR, '..', 'apikey.txt'), 'r', encoding='utf-8') as f:
        environ['OPENAI_API_KEY'] = f.readline().strip('\r\n')


def adapt_latin(s: str) -> str:
    return s.lower() \
        .replace('á', 'a') \
        .replace('à', 'a') \
        .replace('ä', 'a') \
        .replace('ã', 'a') \
        \
        .replace('é', 'e') \
        .replace('è', 'e') \
        .replace('ë', 'e') \
        \
        .replace('í', 'i') \
        .replace('ì', 'i') \
        .replace('ï', 'i') \
        \
        .replace('ó', 'o') \
        .replace('ò', 'o') \
        .replace('ö', 'o') \
        .replace('õ', 'o') \
        \
        .replace('ú', 'u') \
        .replace('ù', 'u') \
        .replace('ü', 'u') \
        \
        .replace('ñ', 'n')
        

def query_gpt(q: str, client: OpenAI, system_role: str = ''):

    if not system_role:
        system_role = variables['CHATGPT_ROLE']
    
    if not q or not q.strip():
        return 'No ha ingresado una consulta.'

    if not messages:
        messages.append(
            {"role": "system", "content": system_role},
        )
        
    messages.append(
        {"role": "user", "content": q}
    )
    
    suspense = '...' if len(system_role) > VARIABLE_CONTENT_PREVIEW else ''
    print_warn('Rol del sistema: ' + f'"{system_role[:VARIABLE_CONTENT_PREVIEW]}{suspense}"')

    completion = client.chat.completions.create(
        model=CURRENT_AI_MODEL,
        messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": q}
        ]
    )
    
    from pprint import pprint
    # pprint(completion.__dict__, indent=4)
    
    return completion.choices[0].message.content

def slugify(t: str):
    valids = string.ascii_letters + string.digits + '_ñÑ'
    
    output = ''
    
    for c in t:
        if c in valids:
            output += c
        else:
            output += '_'
    
    return output

def is_valid_identifier(t: str) -> bool:
    
    if not t: return False
    
    valids = string.ascii_letters + string.digits + '_ñÑ'
    
    if t[0] in string.digits: return False
    
    for c in t:
        if c not in valids:
            return False
    
    return True


def print_err(t: any, end='\n'):
    print(Fore.LIGHTRED_EX + str(t) + Style.RESET_ALL, end=end)


def print_warn(t: any, end='\n'):
    print(Fore.LIGHTYELLOW_EX + str(t) + Style.RESET_ALL, end=end)


def save_vars(name: str, dest_dir = None):

    if not variables:
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
            for k in variables:
                v = variables[k].replace('\n', '\\n').replace('\r', '')
                f.write(f'{k[:MAX_VARIABLE_NAME_LEN]}={v}\n')

        print_warn('Variables guardadas.')

    except Exception as ex:
        import traceback; traceback.print_exc()


def load_vars(name: str, from_dir = None):
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
                variables[ parts[0][:MAX_VARIABLE_NAME_LEN] ] = parts[1] if parts[1] != None else ''

        # Restauramos la ayuda
        variables['SYS_HELP'] = help_str
        variables['ggl'] = '! {BROWSER_PATH} http://www.google.com.ar/search?q='
        variables['wr'] = '! {BROWSER_PATH} https://www.wordreference.com/es/translation.asp?tranword='
        
        print('Variables cargadas.')

    except Exception as ex:
        import traceback; traceback.print_exc()


def saved_vars():
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


def list_vars(q: str):
    
    if q.startswith('v '):
        p_ini = 2
    elif q.startswith('vars '):
        p_ini = 5
    else:
        p_ini = -1
        
    filter = ''
    if p_ini > 0:
        filter = q[p_ini:].lower()
    
    for k in variables:
        if filter:
            if k.lower().find(filter) >= 0:
                _print_preview_variable(k)
        else:
            _print_preview_variable(k)


def run_and_capture_output(cmd: str | list[str]) -> str:
    
    if cmd.lower() in ('cls', 'clear'):
        os.system(cmd)
        return
    
    print_warn(
        '*** Advertencia ***\n' 
        '  Programas de consola que requieran entrada por teclado del usuario,\n'
        '  presentarán fallas visuales y dichas entradas no serán registradas\n'
        '  por esta aplicación.\n') 
    
    proc = subprocess.Popen(
        cmd, 
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        pipesize=1)
    
    acum = ''
    
    while True:
        proc.stdout.flush()
        line = proc.stdout.readline()
        if not line:
            break
        line = line.decode('utf-8', errors='replace')
        print(line, end='')
        acum += line
    
    proc.wait()
    return acum


def list_vars_by_value(q: str):
    
    '''
    Listar variables que contengan el texto buscado.
    '''
    
    if q.startswith('findv '):
        p_ini = 6
        
    filter = adapt_latin(q[p_ini:])
    
    print_warn('Buscando...')
    
    for k in variables:
        if adapt_latin(variables[k]).find(filter) >= 0:
            _print_preview_variable(k)
    
    print_warn('Fin de la búsqueda.')


def load_last_session_vars():
    name = 'last_session.save'
    if not path.exists(path.join(SAVED_SESSIONS_PATH, name)):
        print_warn('No se ha encontrado archvio de variables de la última sesión.')
        return
    load_vars(name, SAVED_SESSIONS_PATH)


def save_last_session_vars():
    name = 'last_session.save'
    save_vars(name, SAVED_SESSIONS_PATH)


def _get_escape_chars_positions(q: str):
    pos_escape_chars = []
    
    cur_pos = 0
    
    while True:
        # Busco el siguiente caracter de escape
        cur_pos = q.find(ESCAPE_CHAR, cur_pos)
        if cur_pos >= 0:
            # Si se el CE está antes del final de la cadena
            if cur_pos < len(q)-1:
                # Si el siguiente caracter NO es un CE
                # Entonces agrego la posición del CE a la lista.
                if q[cur_pos+1] != ESCAPE_CHAR:
                    pos_escape_chars.append(cur_pos)
                
                cur_pos += 2 # 1 para saltar el caracter de escape actual y otro 1 para saltar el caracter escapado
            else:
                # El CE está al final de la cadena, es un error de sintaxis
                # print(Fore.LIGHTRED_EX + 'Carácter de escape al final de la consulta no es válido.' + Style.RESET_ALL)
                # continue
                raise ValueError('Carácter de escape al final de la consulta no es válido.')
        else:
            # No se encontraron CE o ya se recorrió toda la cadena.
            break
    
    return pos_escape_chars


def _get_delimiter1_positions(q: str, pos_escape_chars: list[int]):
    # Extraigo delimitadores de apertura
    pos_delim1 = []
    p1 = -len(delim1)
    while True:
        p1 = q.find(delim1, p1+len(delim1))
        
        # Si se encontró un delimitador
        if p1 >= 0:
            # Veo si el caracter antes del delimitador no es un CE
            if (p1 > 0 and (p1-1 not in pos_escape_chars)) or p1 == 0:
                pos_delim1.append(p1)
        else:
            break
    return pos_delim1


def _get_delimiter2_positions(q: str, pos_escape_chars: list[int]):
    
    # Extraigo delimitadores de cierre
    pos_delim2 = []
    p2 = -len(delim2)
    
    while True:
        p2 = q.find(delim2, p2+len(delim2))
        
        # Si se encontró un delimitador
        if p2 >= 0:
            # Veo si el caracter antes del delimitador no es un CE
            if (p2 > 0 and (p2-1 not in pos_escape_chars)) or p2 == 0:
                pos_delim2.append(p2)
        else:
            break

    return pos_delim2


def _expand_variables(q: str, pos_delim1: list[int], pos_delim2: list[int]):

    # Verifico que estén cerrados todos los delimitadores
    if len(pos_delim1) != len(pos_delim2):
        raise ValueError(f'Hay {abs(len(pos_delim1) - len(pos_delim2))} delimitador(es) de variable(s) no cerrado(s).')

    # Si hay delimitadores a expandir
    if pos_delim1:
        
        # La idea aca es reemplazar los nombres de variables entre delimitadores
        # por sus valores pre asignados.
        
        # Extraigo los caractes que preceden al primer delimitador
        expanded_q = q[:pos_delim1[0]]
    
        # Recorro la lista de posiciones de delimitadores
        for index, p1 in enumerate(pos_delim1):
            # p1 tiene el delimitador de apertura
            # p2 tiene el delim. de cierre correspondiente a p1

            p2 = pos_delim2[index]
            
            # Nombre de la variable
            var_name = q[p1+len(delim1) : p2]
            exp_value = None

            # Valor expandido de la varible
            if var_name in variables:
                exp_value = variables[var_name]
            else:
                raise ValueError(f'Variable no definida: "{var_name}"')
            
            
            # Concateno el valor expandido a la cadena resultante
            expanded_q += exp_value

            # Si hay más delimiatadores iniciales, prosigo
            # a agregar a la salida los caracteres que están 
            # entre el delim final actual y el delim inicial
            # que sigue.
            if index < len(pos_delim1) - 1:
                next_p1 = pos_delim1[index+1]
                expanded_q += q[p2+len(delim2) : next_p1]
            else:
                expanded_q += q[p2+len(delim2) :]
        
        return expanded_q

    # Retorna sin cambios
    return q


def expand_query(q: str):
    
    if delim1 and delim2:

        pos_escape_chars = _get_escape_chars_positions(q)
        pos_delim1 = _get_delimiter1_positions(q, pos_escape_chars)
        pos_delim2 = _get_delimiter2_positions(q, pos_escape_chars)
        expanded_q = _expand_variables(q, pos_delim1, pos_delim2)
        return expanded_q

    # Retorna sin cambios
    return q


def _print_preview_variable(k: str):
    if variables[k] == None:
        variables[k] = ''
        
    if len(variables[k]) > VARIABLE_CONTENT_PREVIEW:
        suspense = '...'
    else:
        suspense = ''
    
    value_preview = variables[k][:VARIABLE_CONTENT_PREVIEW] \
        .replace('\r', '') \
        .replace('\n', ' ')
        
    print(f'    {Fore.LIGHTCYAN_EX}{k}{Style.RESET_ALL} = {value_preview}{suspense}')


# TODO: Pensar en una modalidad para aceptar más de una linea de texto
# para cuando se pegan muchas lineas de texto desde el portapapeles.
#
# while not nl_count >= 2:
#     q = input(Fore.LIGHTGREEN_EX + ' ')
#     print(Style.RESET_ALL + '', end='')
#     if not q:
#         nl_count += 1
#     else:
#         multiline_input += q + '\n'
#         nl_count = 0
# q = multiline_input.strip('\r\n')

def main():
    global CURRENT_AI_MODEL
    global delim1, delim2
    global variables
    global Salir
    global only_chatgpt_mode
    
    prefix = ''
    
    while True:
        print(Fore.LIGHTYELLOW_EX + PROMPT, end='')
        q = input(Fore.LIGHTGREEN_EX + ' ')
        print(Style.RESET_ALL + '', end='')

        if not q.strip():
            print('Escriba sin comillas "help" para ayuda, o presione "S" y luego ENTER para salir.\n')
            continue

        if only_chatgpt_mode:
                        
            if q == '!normalmode':
                only_chatgpt_mode = False
                print_warn('Cambiado a modo de uso normal.')
                continue
            
            # Le agrego el signo de pregunta adelante
            # si ya no lo tiene
            q = ('?' + q) if q[0] != '?' else q
            
        
        if q in ('help', 'ayuda') or q in ('?help', '?ayuda'):
            print(help_str)
            continue

        if q == '!chatgptmode':
            only_chatgpt_mode = True
            print_warn(
                'Cambiado a modo de uso ChatGPT.\n'
                '  Escriba "!normalmode" para volver al modo normal.\n'
                '  Escriba "!S" para salir de la aplicación.\n')
            continue

        if q.startswith('pre '):
            prefix = q[4:]
            continue

        if prefix:
            if not only_chatgpt_mode:
                q = prefix + q

        # if q.startswith(':') and q.find(' ') == -1:
        #     name = slugify(q[1:])[:MAX_VARIABLE_NAME_LEN]
        #     if name in variables:
        #         q = variables[name]
        #         suspense = ''
        #         if len(q) > VARIABLE_CONTENT_PREVIEW:
        #             suspense = '...'
        #         print_warn(f'Interpretando "{q[:VARIABLE_CONTENT_PREVIEW]}{suspense}"')
        #     else:
        #         print_err(f'Variable "{name}" no definida.')
        #         continue

        
        # Interpretar una varaible
        if q.startswith(':'):
            parts = q.split(' ', 1)
            name = slugify(parts[0][1 : 1 + MAX_VARIABLE_NAME_LEN])
            params = parts[1] if len(parts) == 2 else ''
            if name in variables:
                q = variables[name] + params
                suspense = ''
                if len(q) > VARIABLE_CONTENT_PREVIEW:
                    suspense = '...'
                print_warn(f'Interpretando "{q[:VARIABLE_CONTENT_PREVIEW]}{suspense}"')
                # print_warn(f'Interpretando "{q}"...')
            else:
                print_err(f'Variable "{name}" no definida.')
                continue

        # Expandir variable
        try:
            q = expand_query(q)
        except ValueError as ex1:
            print_err(ex1)
            continue
        except Exception as ex:
            import traceback; traceback.print_exc()
            continue

        
        # Establecer rol de chatgpt
        if q.startswith('srol'):
            parts = q.split(' ', 1)
            if parts[0] == 'srol':
                if len(parts) == 2:
                    variables['CHATGPT_ROLE'] = parts[1].strip()
                    print('Ok.')
                else:
                    print_warn(f'El rol actual del asistente es:\n "{variables['CHATGPT_ROLE']}"')
                    
                continue


        # Ejecutar comando de shell
        if q.startswith('! '):
            try:
                variables['lastcmd'] = \
                    run_and_capture_output(q[2:])
            except Exception as ex:
                print_err(ex)                
            continue
        

        # Delimitador 1
        if q.startswith('d1 '):
            delim1 = q[3:]
            if not delim1: delim1 = '{'
            continue

        
        # Delimitador 2
        if q.startswith('d2 '):
            delim2 = q[3:]
            if not delim2: delim2 = '}'
            continue

        
        # Listar variables
        if q in ('v', 'vars') or q.startswith('v ') or q.startswith('vars '):
            list_vars(q)
            continue
        
        
        # Buscar dentro de variables
        if q.startswith('findv '):
            list_vars_by_value(q)
            continue
        
        
        # Copiar una variable a otra
        if q.startswith('cp '):
            parts = q[3:].split(' ')
            if len(parts) != 2:
                print_err('Sintaxis no válida.')
                continue

            if not parts[0] in variables:
                print_err(f'No existe la variable de origen "{parts[0]}".')
                continue

            variables[parts[1]] = variables[parts[0]]
            continue
        
        
        # Renombrar una variable
        if q.startswith('ren '):
            parts = q[4:].split(' ')
            if len(parts) != 2:
                print_err('Sintaxis no válida.')
                continue

            if not parts[0] in variables:
                print_err(f'No existe la variable de origen "{parts[0]}".')
                continue
            
            if parts[1] in variables:
                print_err(f'La variable "{parts[1]}" ya existe. No se renombrará.')
                continue

            variables[parts[1]] = variables[parts[0]]
            del variables[parts[0]]
            continue

        
        
        # Asignar un valor a una variable
        if q.find('=') in range(0, MAX_VARIABLE_NAME_LEN + 1):
            parts = q.split('=', 1)
            name = parts[0].strip()[:MAX_VARIABLE_NAME_LEN]
            if is_valid_identifier(name):
                variables[name] = parts[1] if parts[1] != None else ''
                continue
            

        # Borrar una variable
        if q.startswith('del '):
            name = q[4 : 4+MAX_VARIABLE_NAME_LEN]
            if name in variables:
                del variables[name]
                print_warn(f'Variable "{name}" borrada.')
            else:
                print_err(f'Variable "{name}" no encontrada.')
            continue
        

        # Borrar todas las variables
        if q == 'clearvars':
            variables.clear()
            continue
        
        
        # guardar las variables a un archivo
        if q.startswith('savevars '):
            name = slugify(q[9:])[:MAX_VARIABLE_NAME_LEN] + '.save'
            save_vars(name)
            continue
            

        # cargar variables desde un archivo
        if q.startswith('loadvars '):
            name = slugify(q[9:])[:MAX_VARIABLE_NAME_LEN] + '.save'
            load_vars(name)
            continue
            

        # Lista variables guardadas en archivos
        if q == 'savedvars':
            saved_vars()
            continue


        # Imprime en pantalla una varaible
        if q.startswith('p '):
            name = slugify(q[2:])[:MAX_VARIABLE_NAME_LEN]
            if name in variables:
                print(variables[name])
            else:
                print_err(f'Variable "{name}" no definida.')
            continue


        # Setea modelo de chatgpt
        if q.startswith('setmodel '):
            name = slugify(q[9:])[:100]
            CURRENT_AI_MODEL = name
            continue


        # Sale del sistema
        if q.upper() in ('S', 'SALIR', 'EXIT', '?!S', '?!SALIR', '?!EXIT'):
            print('Hasta luego.\n')
            Salir = True
            return
        
        
        # Consulta a chatgpt
        if q.startswith('?'):
            variables['lastq'] = q[1:]
            print_warn('Esperando respuesta de ChatGPT...')
            r = query_gpt(q, client)
            variables['lastr'] = r
            print(r)
            continue
        
        
        print_err(f'Comando incompleto o no reconocido: "{q}"')
        continue
        
        
if __name__ == '__main__':

    # Initialize colorama
    init()

    print('Cargando APIKEY...')
    load_apikey()
    
    print('Inicializando cliente OpenAI...')
    client = OpenAI()
    
    try:
        load_last_session_vars()
    except Exception as ex:
        import traceback; traceback.print_exc()

    while not Salir:
        try:
            main()
        except Exception as ex:
            import traceback; traceback.print_exc()
        finally:
            save_last_session_vars()
