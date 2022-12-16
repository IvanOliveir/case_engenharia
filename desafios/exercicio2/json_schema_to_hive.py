_ATHENA_CLIENT = None

def create_hive_table_with_athena(query):
    '''
    Função necessária para criação da tabela HIVE na AWS
    :param query: Script SQL de Create Table (str)
    :return: None
    '''
    
    print(f"Query: {query}")
    _ATHENA_CLIENT.start_query_execution(
        QueryString=query,
        ResultConfiguration={
            'OutputLocation': f's3://iti-query-results/'
        }
    )

def handler():
    '''
    #  Função principal
    Aqui você deve começar a implementar o seu código
    Você pode criar funções/classes à vontade
    Utilize a função create_hive_table_with_athena para te auxiliar
        na criação da tabela HIVE, não é necessário alterá-la
    '''
    import json
    import json_to_sql

    #Open the schema file
    with open('schema.json') as json_file:
        json_schema = json.load(json_file)

    #Apply a recursively function to extract the names and types of the fields
    cols_type = json_to_sql._build_query('properties', json_schema)

    #Build the Athena query
    query = f"CREATE EXTERNAL TABLE IF NOT EXISTS {json_to_sql.TABLE_NAME}({cols_type})" \
            f"LOCATION 's3://iti-query-results/'"

    #Run the query on Athena
    create_hive_table_with_athena(query)