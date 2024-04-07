from utils import _multi_line_input, is_valid_identifier, print_err, print_warn


def preprocess_chatgpt_mode(parent, q) -> str:
    
    if parent.only_chatgpt_mode:
        # Le agrego el signo de pregunta adelante
        # si ya no lo tiene
        q = ('?' + q) if q[0] != '?' else q            
        
    return q
            
            
def set_chatgpt_mode(parent):
    parent.only_chatgpt_mode = True
    print_warn(
        'Cambiado a modo de uso ChatGPT.\n'
        '  Escriba "!normalmode" para volver al modo normal.\n'
        '  Escriba "!S" para salir de la aplicación.\n')
    
    
def multi_line_input(parent, q):
    q_parts = q.split(' ', 2)
    if len(q_parts) != 3:
        print_err('Sintaxis no válida.')
        return
    
    dest_var = q_parts[1] or None
    
    if not is_valid_identifier(dest_var):
        print_err('Sintaxis no válida: El nombre de la varaible de destino no es válido.')
        return
    
    end_delim = q_parts[2] or None
    if end_delim:
        parent.variables[dest_var] = _multi_line_input(end_delimiter=end_delim)
    else:
        parent.variables[dest_var] = _multi_line_input()
        
        
def set_gpt_role(parent, q):
    parts = q.split(' ', 1)
    if parts[0] == 'srol':
        variables = parent.variables
        if len(parts) == 2:
            variables['CHATGPT_ROLE'] = parts[1].strip()
            print('Ok.')
        else:
            print_warn(f'El rol actual del asistente es:\n "{variables['CHATGPT_ROLE']}"')
            
            
def execute_shell_command(parent, q):
    try:
        parent.variables['lastcmd'] = \
            parent.vars_comm_handlers.run_and_capture_output(q[2:])
    except Exception as ex:
        print_err(ex)