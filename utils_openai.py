from constant import APIKEY_FILE_PATH, VARIABLE_CONTENT_PREVIEW

from openai import OpenAI
from os import environ

from utils import print_err, print_warn


class OpenAIWrapper:

    variables: dict = None
    CURRENT_AI_MODEL: str = None
    
    # OpenAI Client
    client = None
    
    # Lista de conversación con ChatGPT
    messages = []

    def __init__(
      self, 
      variables: dict,
      current_ai_model: str):
        
        self.variables = variables
        self.CURRENT_AI_MODEL = current_ai_model
        
        
    def connect_openai(self):
        try:
            print('Cargando APIKEY...')
            self.load_apikey()
        
            print('Inicializando cliente OpenAI...')
            self.client = OpenAI()
            return True
        except Exception as ex:
            import traceback; traceback.print_exc();
            print_err('No se ha podido inicializar cliente OpenAI.')
            return False

    
    def load_apikey(self):
        with open(APIKEY_FILE_PATH, 'r', encoding='utf-8') as f:
            environ['OPENAI_API_KEY'] = f.readline().strip('\r\n')


    def query_gpt(self, q: str, system_role: str = ''):

        if not self.client:
            if not self.connect_openai():
                return
            
        client = self.client
        
        if not system_role:
            system_role = self.variables['CHATGPT_ROLE']
        
        if not q or not q.strip():
            return 'No ha ingresado una consulta.'

        if not self.messages:
            self.messages.append(
                {"role": "system", "content": system_role},
            )
            
        self.messages.append(
            {"role": "user", "content": q}
        )
        
        suspense = '...' if len(system_role) > VARIABLE_CONTENT_PREVIEW else ''
        print_warn('Rol del sistema: ' + f'"{system_role[:VARIABLE_CONTENT_PREVIEW]}{suspense}"')

        completion = client.chat.completions.create(
            model=self.CURRENT_AI_MODEL,
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": q}
            ]
        )
        
        from pprint import pprint
        # pprint(completion.__dict__, indent=4)
        
        return completion.choices[0].message.content
