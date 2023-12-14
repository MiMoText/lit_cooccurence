import pandas as pd
import math
import numpy as np
import plotly.graph_objects as go

# Load and clean data
df = pd.read_csv("work_title.tsv", sep="\t")
df = df[df.type == "Literary work"]
df = df[df.Identifier.notnull()]
df = df[df.MiMoTextBase_ID.notnull()]

# Create a list of all unique literary works
all_litworks = df.Identifier.unique().tolist()

# Initialize an index dictionary for literary works
litwork_index = dict()

# Iterate over the rows to populate the index
for _, row in df.iterrows():
    litwork_id = row['Identifier']
    text = row['text']

    # Check if the literary work is in the index
    if litwork_id not in litwork_index:
        litwork_index[litwork_id] = dict()
    
    # Add sentence to the set for the specific text
    if text not in litwork_index[litwork_id]:
        litwork_index[litwork_id][text] = set()
    
    litwork_index[litwork_id][text].add(int(row['sentence']))

# get the sum of the biggest sentence number for each text
sent_count = 12151
text_count = len(df.text.unique())

sentence_windows = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50,100]

for window_size in sentence_windows:
    cooccurrences = {}
    n = len(litwork_index)
    npmi_matrix = np.zeros((n, n))
    for lit1, sec1s in litwork_index.items():
        for lit2, sec2s in litwork_index.items():
            if lit1 != lit2:
                for sec1, sent1s in sec1s.items():
                    for sec2, sent2s in sec2s.items():
                        if sec1 == sec2:
                            for sent1 in sent1s:
                                for sent2 in sent2s:
                                    if abs(sent1 - sent2) < window_size:
                                        if lit1 not in cooccurrences:
                                            cooccurrences[lit1] = dict()
                                        if lit2 not in cooccurrences[lit1]:
                                            cooccurrences[lit1][lit2] = 0
                                        cooccurrences[lit1][lit2] += 1
    
                if lit1 not in cooccurrences:
                    cooccurrences[lit1] = dict()
                if lit2 not in cooccurrences[lit1]:
                    cooccurrences[lit1][lit2] = 0
                n1 = 0
                for sec in litwork_index[lit1]:
                    n1 += len(litwork_index[lit1][sec])
                n2 = 0
                for sec in litwork_index[lit2]:
                    n2 += len(litwork_index[lit2][sec])
                p_work1 = n1 / (sent_count-text_count*window_size+text_count)
                p_work2 = n2 / (sent_count-text_count*window_size+text_count)
                p_occurrence = cooccurrences[lit1][lit2] / (sent_count-text_count*window_size+text_count)
                if p_occurrence == 0:  # Avoid log(0) and division by zero
                    npmi = 0
                else:
                    pmi = math.log2(p_occurrence) - math.log2(p_work1) - math.log2(p_work2 + 0.5)
                    npmi = pmi / -math.log2(p_occurrence)
                npmi_matrix[all_litworks.index(lit1)][all_litworks.index(lit2)] = npmi
                npmi_matrix[all_litworks.index(lit2)][all_litworks.index(lit1)] = npmi
    # Assuming npmi_matrix is already computed and is a numpy array
    x_labels = all_litworks
    y_labels = all_litworks
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
        title=f'nPMI Heatmap (work cooccurrence in {str(window_size)} sentences)',
        xaxis_nticks=100,
        yaxis_nticks=100,
        xaxis_title=f'work 1',
        yaxis_title=f'work 2',
        margin=dict(l=150, r=5, t=45, b=120)
    )
    # Export to HTML
    fig.write_html(f'npmi_heatmap_work_{str(window_size)}.html')
