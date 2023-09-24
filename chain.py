from langchain.llms import AI21
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser

# output parser for columns names mapping
class ColumnsNamesMapParser(BaseOutputParser):
  def parse(self, text):
    mapping_pairs = []
    for string in text.split("\n")[1:]:
      source_name, _, target_name = string.split(" ")
      mapping_pairs.append((source_name, target_name))
    return mapping_pairs

# output parser for genereated values format mapping code
class CodeParser(BaseOutputParser):
  def parse(self, text):
    apost_count = 0
    name_saved = False

    func_name = ''
    code = ''

    for char in text:
      if char == '(' and not name_saved:
        func_name = code
        func_name = func_name.replace('\n', '')
        func_name = func_name[4:]
        name_saved = True
      if char == '`':
        apost_count += 1

        if apost_count == 6:
          break

      else:
        code += char

    return func_name, code


class NamesMappingChain:
    def __init__(self) -> None:
        self.__promp_templ = PromptTemplate.from_template('You are solving table format mapping task. For every column from the source table with provided provided (column_name, column_values) pairs: {source_name_values_pairs}. ' +
                                                           'Find corresponding column in the target table with provided (column_name, column_values) pairs: {target_name_values_pairs}. ' +
                                                           'Give response in format: source_column_name -> target_column_name. Return only mapped pairs and nothing more.')
        self.__model = AI21(ai21_api_key='rYbX8fTQPGyeB94y2IxnCDzMuHyQlQwK')
        self.__out_parser = ColumnsNamesMapParser()

        self.__chain = self.__promp_templ | self.__model | self.__out_parser
    
    def response(self, source_name_values_pairs, target_name_values_pairs):
         return self.__chain.invoke({'source_name_values_pairs': source_name_values_pairs, 'target_name_values_pairs': target_name_values_pairs})
    

class CodeGenaratingChain:
    def __init__(self) -> None:
        self.__promp_templ = PromptTemplate.from_template('You are programmer solving task of mapping data from various sources in exel tables. ' +
                                                  'Provided values of source format: {source_format} from column {source_column} of the source table ' +
                                                  'and values of target format: {target_format} from column {target_column} of the template table. '+
                                                  'Write correct python code for a function that takes value in the source format as input ' +
                                                  'and convert it exactly to the value in the target format.')# +
                                                  #'Written function must return values exactly in target format: {target_format} only if conversion is needed, ' +
                                                  #'otherwise written function must return values exactly in format: {source_format}. ' +
                                                  #'So all returned values must have only source format: {source_format} or only target format: {target_format}.')
        self.__model = AI21(ai21_api_key='rYbX8fTQPGyeB94y2IxnCDzMuHyQlQwK')
        self.__out_parser = CodeParser()

        self.__chain = self.__promp_templ | self.__model | self.__out_parser
    
    def response(self, source_format, source_column, target_format, target_column):
         return self.__chain.invoke({'source_format': source_format, 'source_column': source_column, 'target_format': target_format, 'target_column': target_column})