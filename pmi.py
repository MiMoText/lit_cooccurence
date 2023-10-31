import pandas as pd
import math
import numpy as np

df = pd.read_csv("work_title.tsv", sep="\t")
df = df[df.type == "Literary work"]
#remove the rows where identifier is empty
df = df[df.Identifier.notnull()]
df = df[df.MiMoTextBase_ID.notnull()]

all_works = df.Identifier.unique().tolist() #get a list of all mentioned literary works
work_index = dict() #get a index of secondary works for each literary work
for work in all_works:
    work_index[work] = set()

unique_text = df.text.unique() #get a list of all secondary works


for title in unique_text:
    ner_list = df[df.text == title].Identifier.unique() #get a list of unique literary works mentioned in the secondary work
    for work in all_works:
        if work in ner_list:
            work_index[work].add(title)

# for title in unique_text:
#     for sentence in df[df.text == title].sentence.unique():
#         ner_list = df[df.text == title][df.sentence == sentence].Identifier.unique() #get a list of unique literary works mentioned in the secondary work
#         for work in all_works:
#             if work in ner_list:
#                 work_index[work].add(title+"_"+str(sentence))

n = len(all_works)
npmi_matrix = np.zeros((n, n))

for i in range(n):
    for j in range(i+1, n):  # Only compute upper triangle, since matrix is symmetric
        p_work1 = len(work_index[all_works[i]]) / len(unique_text)
        p_work2 = len(work_index[all_works[j]]) / len(unique_text)
        p_occurrence = len(work_index[all_works[i]].intersection(work_index[all_works[j]])) / len(unique_text)
        
        if p_occurrence == 0:  # Avoid log(0) and division by zero
            npmi = 0
        else:
            pmi = math.log2(p_occurrence) - math.log2(p_work1) - math.log2(p_work2 + 0.5)
            npmi = pmi / -math.log2(p_occurrence)

        npmi_matrix[i][j] = npmi
        npmi_matrix[j][i] = npmi

#plot matrix as heatmap
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
ax = sns.heatmap(npmi_matrix, xticklabels=all_works, yticklabels=all_works)
plt.show()



#find all pairs of items of all_works
# pmi_result = dict()
# for i in range(len(all_works)):
#     for j in range(i+1, len(all_works)):
#         p_work1 = len(work_index[all_works[i]])/len(unique_text)
#         p_work2 = len(work_index[all_works[j]])/len(unique_text)
#         p_occurrence = len(work_index[all_works[i]].intersection(work_index[all_works[j]]))/len(unique_text)
#         pmi = math.log2(p_occurrence+0.5/((p_work1+0.5)*(p_work2+0.5)))
#         npmi = pmi/-math.log2(p_occurrence+0.5)
#         #print(all_works[i], all_works[j],npmi)
#         pmi_result[(all_works[i], all_works[j])] = npmi

# #write the result to a file
# with open("pmi_result.tsv", "w",encoding="utf-8") as f:
#     for key, value in pmi_result.items():
#         f.write("%s\t%s\t%s\n"%(key[0], key[1], value))