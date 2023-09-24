import sys
import pandas as pd

from extractor import TableDataExtractor
from chain import NamesMappingChain, CodeGenaratingChain

if __name__ == '__main__':
    filepaths = {}
    for i in range(len(sys.argv[1:])):
        if sys.argv[i] == '--source':
            filepaths['source'] = sys.argv[i+1] # path to source table
        elif sys.argv[i] == '--template':
            filepaths['template'] = sys.argv[i+1] # path to template table
        elif sys.argv[i] == '--target':
            filepaths['target'] = sys.argv[i+1] # path where to save target table

    if set(['source', 'template', 'target']) != set(filepaths.keys()):
        print('Incorrect console arguments. Please enter after \'main.py\': --source [path to source table], --template [path to template table] and --target [path to save target table]') 
        sys.exit()

    source_extractor = TableDataExtractor(filepaths['source'])
    template_extractor = TableDataExtractor(filepaths['template'])
    names_mapper = NamesMappingChain()
    code_generator = CodeGenaratingChain()

    # dataframes from provided csv files
    template_df = template_extractor.get_df()
    target_df = pd.DataFrame(columns=template_df.columns)
    source_df = source_extractor.get_df()

    # number of row in dataframes provided in prompts
    num_values = min(10, len(template_df))

    # prompt arguments for NamesMappingChain
    source_name_values_pairs = source_extractor.get_name_values_pairs(num_values)
    target_name_values_pairs = template_extractor.get_name_values_pairs(num_values)

    print('Columns names mapping...')

    # handling random errors in output format (source_column_name -> target_column_name)
    for _ in range(15):
        try:
            # if exception occurs break is skipped
            names_map_list = names_mapper.response(source_name_values_pairs, target_name_values_pairs)

            assert len(names_map_list) == len(template_df.columns)

            # if no exception occurs continue execution after while block
            break
        except (Exception):
            print('Incorrectly generated ouput fomat. Regenerating...')
            #names_map_list = names_mapper.response(source_name_values_pairs, target_name_values_pairs)

    print('Columns names mapped.', end='\n\n\n')
    print(f'Mapping source table {filepaths["source"]} to target table {filepaths["target"]}')

    # mapping values formats
    for source_column, target_column in names_map_list:
        print(f'Generating code for mapping values from format of {source_column} to the format of {target_column}')

        # prompt arguments for CodeGenaratingChain
        source_format = source_extractor.get_column_values_string(source_column, num_values)
        target_format = template_extractor.get_column_values_string(target_column, num_values)
        
        # code might be generated with errors, regenerating up to 10 times while it is incorrect
        for _ in range(20):
            try:
                macros_name, macros = code_generator.response(source_format, source_column, target_format, target_column)

                # for syntactic errors
                exec(macros)
                eval(macros_name)

                # for semantic errors
                #for i in range(min(2 * num_values, len(source_df))):
                    #assert abs(len(str(eval(macros_name)(source_df[source_column][i]))) - len(str(template_df[target_column][i]))) < 6

                target_df[target_column] = source_df[source_column].map(eval(macros_name))
                
                # if no exception occurs continue execution after while block
                break
            except Exception:
                print('Error in generated function. Regenerating...')
                

        print(f'Column {source_column} mapped.', end='\n\n')
    
    print(f'Source table {filepaths["source"]} mappet to the target table {filepaths["target"]}')
    target_df.to_csv(path_or_buf=filepaths['target'])
