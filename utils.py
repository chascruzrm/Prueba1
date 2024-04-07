import string
from colorama import Fore, Back, Style, init

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


def _multi_line_input(end_delimiter = '/eof'):
        
    multiline_input = ''
    
    prompt = Fore.LIGHTGREEN_EX + f'Pegue texto. Finalize con {end_delimiter}:' + Style.RESET_ALL
    print(prompt)
    
    while True:
        q = input('')

        if q == end_delimiter:
            break
        else:
            multiline_input += q + '\n'
            
    return multiline_input.strip()
