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
    
    - mli <nombre_var_destino> <delim_fin_captura> - Captura texto con múltiples líneas hasta 
                                                     que la última linea sea igual al texto
                                                     delimitador de fin.
    
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
