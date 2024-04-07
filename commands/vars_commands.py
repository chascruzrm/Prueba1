import os
import subprocess

from constant import ESCAPE_CHAR, MAX_VARIABLE_NAME_LEN, VARIABLE_CONTENT_PREVIEW
from utils import adapt_latin, is_valid_identifier, print_err, print_warn, slugify
from colorama import Fore, Back, Style, init

class VarsCommands:
    
    '''
    Clase para administrar asuntos de variables de usuario
    '''
    
    variables = None
    
    # Variable interpolation delimiters
    # User can access its variables by referencing them in prompts
    delim1 = None
    delim2 = None
    
    
    def __init__(
      self,
      variables: dict,
      delim1: str = '{',
      delim2: str = '}'):
        
        self.variables = variables
        self.delim1 = delim1 or '{'
        self.delim2 = delim2 or '}'

    def list_vars(self, q: str):
        
        if q.startswith('v '):
            p_ini = 2
        elif q.startswith('vars '):
            p_ini = 5
        else:
            p_ini = -1
            
        filter = ''
        if p_ini > 0:
            filter = q[p_ini:].lower()
        
        for k in self.variables:
            if filter:
                if k.lower().find(filter) >= 0:
                    self._print_preview_variable(k)
            else:
                self._print_preview_variable(k)
                
                
    def run_variable_content(self, q):
        parts = q.split(' ', 1)
        name = slugify(parts[0][1 : 1 + MAX_VARIABLE_NAME_LEN])
        params = parts[1] if len(parts) == 2 else ''
        if name in self.variables:
            q = self.variables[name] + params
            suspense = ''
            if len(q) > VARIABLE_CONTENT_PREVIEW:
                suspense = '...'
            print_warn(f'Interpretando "{q[:VARIABLE_CONTENT_PREVIEW]}{suspense}"')
            # print_warn(f'Interpretando "{q}"...')
            return q
        else:
            print_err(f'Variable "{name}" no definida.')
        
        return None


    def run_and_capture_output(self, cmd: str | list[str]) -> str:
        
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


    def list_vars_by_value(self, q: str):
        
        '''
        Listar variables que contengan el texto buscado.
        '''
        
        if q.startswith('findv '):
            p_ini = 6
            
        filter = adapt_latin(q[p_ini:])
        
        print_warn('Buscando...')
        
        for k in self.variables:
            if adapt_latin(self.variables[k]).find(filter) >= 0:
                self._print_preview_variable(k)
        
        print_warn('Fin de la búsqueda.')


    def _get_escape_chars_positions(self, q: str):
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


    def _get_delimiter1_positions(self, q: str, pos_escape_chars: list[int]):
        # Extraigo delimitadores de apertura
        pos_delim1 = []
        p1 = -len(self.delim1)
        while True:
            p1 = q.find(self.delim1, p1+len(self.delim1))
            
            # Si se encontró un delimitador
            if p1 >= 0:
                # Veo si el caracter antes del delimitador no es un CE
                if (p1 > 0 and (p1-1 not in pos_escape_chars)) or p1 == 0:
                    pos_delim1.append(p1)
            else:
                break
        return pos_delim1


    def _get_delimiter2_positions(self, q: str, pos_escape_chars: list[int]):
        
        # Extraigo delimitadores de cierre
        pos_delim2 = []
        p2 = -len(self.delim2)
        
        while True:
            p2 = q.find(self.delim2, p2+len(self.delim2))
            
            # Si se encontró un delimitador
            if p2 >= 0:
                # Veo si el caracter antes del delimitador no es un CE
                if (p2 > 0 and (p2-1 not in pos_escape_chars)) or p2 == 0:
                    pos_delim2.append(p2)
            else:
                break

        return pos_delim2


    def _expand_variables(self, q: str, pos_delim1: list[int], pos_delim2: list[int]):

        variables = self.variables
        delim1 = self.delim1
        delim2 = self.delim2
        
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
                
                if not is_valid_identifier(var_name):
                    expanded_q += delim1 + var_name + delim2
                    if index < len(pos_delim1) - 1:
                        next_p1 = pos_delim1[index+1]
                        expanded_q += q[p2+len(delim2) : next_p1]
                    else:
                        expanded_q += q[p2+len(delim2) :]
                    continue
                
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


    def expand_query(self, q: str):
        
        delim1 = self.delim1
        delim2 = self.delim2
        
        if delim1 and delim2:

            pos_escape_chars = self._get_escape_chars_positions(q)
            pos_delim1 = self._get_delimiter1_positions(q, pos_escape_chars)
            pos_delim2 = self._get_delimiter2_positions(q, pos_escape_chars)
            expanded_q = self._expand_variables(q, pos_delim1, pos_delim2)
            return expanded_q

        # Retorna sin cambios
        return q


    def _print_preview_variable(self, k: str):
        
        variables = self.variables
        
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
        
        
        
    def print_var(self, q):
        name = slugify(q[2:])[:MAX_VARIABLE_NAME_LEN]
        if name in self.variables:
            for c in self.variables[name]:
                print(c, end='')
            print()
        else:
            print_err(f'Variable "{name}" no definida.')
        
        
    def copy_var(self, q):
        parts = q[3:].split(' ')
        if len(parts) != 2:
            print_err('Sintaxis no válida.')
            return

        if not parts[0] in self.variables:
            print_err(f'No existe la variable de origen "{parts[0]}".')
            return

        self.variables[parts[1]] = self.variables[parts[0]]
        
        
    def rename_var(self, q):
        parts = q[4:].split(' ')
        if len(parts) != 2:
            print_err('Sintaxis no válida.')
            return

        if not parts[0] in self.variables:
            print_err(f'No existe la variable de origen "{parts[0]}".')
            return
        
        if parts[1] in self.variables:
            print_err(f'La variable "{parts[1]}" ya existe. No se renombrará.')
            return

        self.variables[parts[1]] = self.variables[parts[0]]
        del self.variables[parts[0]]
        
        
    def del_var(self, q):
        name = q[4 : 4+MAX_VARIABLE_NAME_LEN]
        if name in self.variables:
            del self.variables[name]
            print_warn(f'Variable "{name}" borrada.')
        else:
            print_err(f'Variable "{name}" no encontrada.')