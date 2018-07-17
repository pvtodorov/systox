import pandas as pd
import os

# using the merged_medianData.csv create dose-response files for each compound

infolder = '../data/processed_data/01/LISS/01/'
outfolder = '../data/processed_data/01/LISS/02/'

if not os.path.exists(outfolder):
    os.makedirs(outfolder)

geneList = pd.read_csv('../data/lists/gene_list.csv')
genes = geneList['Gene'].tolist()
data = pd.read_csv(infolder + 'merged_medianData.csv')
df0 = data
cmpMetas_cols = ['CMP', 'DOSES']
cmpMetas = pd.DataFrame(columns=cmpMetas_cols)
compounds = data['CMP'].unique().tolist()
times = [6, 24]
df0 = data
cmpMetas_cols = ['CMP', 'DOSES']
cmpMetas = pd.DataFrame(columns=cmpMetas_cols)
compounds = data['CMP'].unique().tolist()
times = [6, 24]

# the control compounds do not have a dose responses
# this is because there is only one 'dose' for each compound
# the dose-response files must still be generated for future computations
control_compounds = ['DMSO_0.5pct', 'DMSO_0.1pct', 'Medium']

# generate dose responses for all compounds except controls
for i in times:
    df1 = df0[df0['TIME'] == i]
    df1 = df1[~df1['CMP'].isin(control_compounds)]
    for j in compounds:
        df2 = df1[df1['CMP'] == j]
        df2 = df2.sort_values('DOSE', axis=0, ascending=True, inplace=False,
                              kind='quicksort', na_position='last')
        tempMetas = pd.DataFrame(columns=cmpMetas_cols)
        tempMetas['CMP'] = [j]
        doses = df2['DOSE'].tolist()
        tempMetas['DOSES'] = [doses]
        cmpMetas = cmpMetas.append(tempMetas)
        dosecourse_cols = ['GENE', '1', '2', '3', '4', '5', '6']
        dosecourse = pd.DataFrame(columns=dosecourse_cols)
        for m in genes:
            dosecourseTemp = pd.DataFrame(columns=dosecourse_cols)
            dosecourseTemp['GENE'] = [m]
            geneValues = df2[m].tolist()
            geneValueDoseDict = dict(zip(['1', '2', '3', '4', '5', '6'],
                                     geneValues))
            for k in geneValueDoseDict:
                dosecourseTemp[k] = [geneValueDoseDict[k]]
            dosecourse = dosecourse.append(dosecourseTemp)
        file = j + '_' + str(i) + 'h'
        dosecourse.to_csv((outfolder + file + '.csv'), index=False)
    cmpMetas = cmpMetas.drop_duplicates('CMP')
    cmpMetas.to_csv(outfolder + 'cmpMetas.csv', index=False)

# generate dose responses for control compounds
for i in times:
    df1 = df0[df0['TIME'] == i]
    for j in (control_compounds):
        df2 = df1[df1['CMP'] == j]
        df2 = df2.sort_values('DOSE', axis=0, ascending=True, inplace=False,
                              kind='quicksort', na_position='last')
        dosecourse_cols = ['GENE', '1', '2', '3', '4', '5', '6']
        dosecourse = pd.DataFrame(columns=dosecourse_cols)
        dosecourse['GENE'] = genes
        for k in range(1, 7):
            dosecourse[str(k)] = df2[genes].reset_index(drop=True)\
                                           .values[0].tolist()
            file = j + '_' + str(i) + 'h'
            dosecourse.to_csv((outfolder + file + '.csv'), index=False)
