import pandas as pd

# class for extraction and storing table data and metadata in string format
class TableDataExtractor:
  def __init__(self, filepath):
    self._filepath = filepath
    self.load()

  def load(self):
    self.__table = pd.read_csv(self._filepath)
    self.__column_names = self.__table.columns
  
  def get_column_names(self):
    return self.__column_names

  def get_column_values(self, column_name, num_values):
    return self.__table[column_name][:num_values]

  def get_column_values_string(self, column_name, num_values):
    result = ''
    for value in self.get_column_values(column_name, num_values):
      result += str(value) + ', '
    return result[:-2]

  def get_name_values_pairs(self, num_values):
    result = ''
    for column in self.get_column_names():
      result += column + ': ' + self.get_column_values_string(column, num_values) +'; '
    
    return result[:-2]
  
  def get_df(self):
    return self.__table