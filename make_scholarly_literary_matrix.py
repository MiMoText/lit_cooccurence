import pandas as pd

file_path = 'work_title.tsv'

df = pd.read_csv(file_path, sep='\t', usecols=['text', 'Identifier', 'MiMoTextBase_ID'])

df = df[df['MiMoTextBase_ID'].notnull()]

grouped_df = df.groupby(['MiMoTextBase_ID', 'Identifier', 'text']).size().reset_index(name='frequency')

pivot_table = grouped_df.pivot_table(index=['MiMoTextBase_ID', 'Identifier'], 
                                     columns='text', 
                                     values='frequency', 
                                     fill_value=0)

pivot_table.to_csv('scholarly_literary_matrix.csv', sep='\t')