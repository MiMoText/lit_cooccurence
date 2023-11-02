import pandas as pd
import math
import numpy as np
import plotly.graph_objects as go

umfang = "text" # set it to "sentence" in order to get only the cooccurrence in the same sentence
unit = "author" # alternatively set it to "work"

df = pd.read_csv("work_title.tsv", sep="\t")
df = df[df.type == "Literary work"]
#remove the rows where identifier is empty
df = df[df.Identifier.notnull()]
df = df[df.MiMoTextBase_ID.notnull()]

def get_author(s):
    return s.split("_")[-1]

if unit == "author":
    df['Identifier'] = df['Identifier'].apply(get_author)

all_units = df.Identifier.unique().tolist() #get a list of all mentioned literary works
work_index = dict() #get a index of secondary works for each literary work
for work in all_units:
    work_index[work] = set()

unique_text = df.text.unique() #get a list of all secondary works

for title in unique_text:
    if umfang == "text":
        ner_list = df[df.text == title].Identifier.unique() #get a list of unique literary works mentioned in the secondary work
        for work in all_units:
            if work in ner_list:
                work_index[work].add(title)
    else:
        for sentence in df[df.text == title].sentence.unique():
            ner_list = df[df.text == title][df.sentence == sentence].Identifier.unique()
            for work in all_units:
                if work in ner_list:
                    work_index[work].add(title+"_"+str(sentence))

n = len(all_units)
npmi_matrix = np.zeros((n, n))

for i in range(n):
    for j in range(i+1, n):  # Only compute upper triangle, since matrix is symmetric
        p_work1 = len(work_index[all_units[i]]) / len(unique_text)
        p_work2 = len(work_index[all_units[j]]) / len(unique_text)
        p_occurrence = len(work_index[all_units[i]].intersection(work_index[all_units[j]])) / len(unique_text)
        
        if p_occurrence == 0:  # Avoid log(0) and division by zero
            npmi = 0
        else:
            pmi = math.log2(p_occurrence) - math.log2(p_work1) - math.log2(p_work2 + 0.5)
            npmi = pmi / -math.log2(p_occurrence)

        npmi_matrix[i][j] = npmi
        npmi_matrix[j][i] = npmi

# Assuming npmi_matrix is already computed and is a numpy array
x_labels = all_units
y_labels = all_units

custom_colorscale = [
    [0.0, 'rgb(255,255,255)']
]

fig = go.Figure(data=go.Heatmap(
                    z=npmi_matrix,
                    x=x_labels,
                    y=y_labels,
                    colorscale=custom_colorscale,
                    zmin=-1,  # Assuming the NPMI values range from -1 to 1
                    zmax=1,
                    colorbar=dict(ticktext=['No Cooccurrence'])
                    ))

# Update layout to make it more readable
fig.update_layout(
    title=f'nPMI Heatmap ({unit} cooccurrence in {umfang})',
    xaxis_nticks=100,
    yaxis_nticks=100,
    xaxis_title=f'{unit} 1',
    yaxis_title=f'{unit} 2',
    margin=dict(l=150, r=5, t=45, b=120)
)

# Export to HTML
fig.write_html(f'npmi_heatmap_{unit}_{umfang}.html')

#find all pairs of items of all_units
# pmi_result = dict()
# for i in range(len(all_units)):
#     for j in range(i+1, len(all_units)):
#         p_work1 = len(work_index[all_units[i]])/len(unique_text)
#         p_work2 = len(work_index[all_units[j]])/len(unique_text)
#         p_occurrence = len(work_index[all_units[i]].intersection(work_index[all_units[j]]))/len(unique_text)
#         pmi = math.log2(p_occurrence+0.5/((p_work1+0.5)*(p_work2+0.5)))
#         npmi = pmi/-math.log2(p_occurrence+0.5)
#         #print(all_units[i], all_units[j],npmi)
#         pmi_result[(all_units[i], all_units[j])] = npmi

# #write the result to a file
# with open("pmi_result.tsv", "w",encoding="utf-8") as f:
#     for key, value in pmi_result.items():
#         f.write("%s\t%s\t%s\n"%(key[0], key[1], value))