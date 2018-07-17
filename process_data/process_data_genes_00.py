import pandas as pd
import os

# read the LISS L1000 files and create fold-change csvs

infolder = '../data/original_data/LISS/NORM/'
outfolder = '../data/processed_data/01/LISS/00/'

if not os.path.exists(outfolder):
    os.makedirs(outfolder)

normfiles = os.listdir(infolder)
normfiles = [x for x in normfiles if x[-4:] == '.gct']
normnames = [x[0: (len(x) - 4)] for x in normfiles]

FC = pd.DataFrame()

for nfile in normfiles:
    # these files have different structures and we have to manually specify
    # where the metadata ends for each one ends so we can grab just the data
    # we end up dropping the meta and restoring it later
    if 'KTOX001' in nfile:
        endmeta = 34
    if 'KTOX002' in nfile:
        endmeta = 28
    df0 = pd.read_table(infolder + nfile, skiprows=[0, 1])
    columns = df0.columns.tolist()
    datacolumns = [x for x in columns if 'KTOX' in x]
    genes = df0['pr_gene_symbol'].tolist()
    genes = [x for x in genes if (x != 'na')]
    data = df0[datacolumns]
    data = data.drop(data.index[0:(endmeta + 1)])
    data['pr_gene_symbol'] = genes
    data = data[['pr_gene_symbol'] + datacolumns]
    data = data.set_index('pr_gene_symbol')
    data = data.transpose()
    data = data.reset_index()
    datacolumnsTrans = data.columns.tolist()
    datacolumnsTrans.remove('index')
    metas = df0[0:endmeta + 1]
    metas = metas[['id'] + datacolumns]
    metas = metas.reset_index(drop=True)
    metas = metas.set_index('id')
    metas = metas.transpose()
    metas = metas.reset_index()
    metacolumnsTrans = metas.columns.tolist()
    metacolumnsTrans.remove('index')
    new = data.merge(metas, how='outer', on='index')
    new = new[['index'] + metacolumnsTrans + genes]
    ctl_vehicle = new[new['pert_type'] == 'ctl_vehicle']
    ctl_vehicle = ctl_vehicle[genes]
    ctl_vehicle = (ctl_vehicle.astype(float))
    dmso_mean = ctl_vehicle.mean().tolist()
    dmso_std = ctl_vehicle.std().tolist()
    new_genes = (new[genes].astype(float)).as_matrix()
    # why am I raising the difference to a power of two here?
    # the LISS data is in the format of Log2(FC)
    # This operation turns it into FC
    dmso_FC = (2**(new_genes - dmso_mean))
    dmso_FC_data = pd.DataFrame(data=dmso_FC,
                                index=datacolumns,
                                columns=genes)
    dmso_FC_data = dmso_FC_data.reset_index()
    dmso_FC_table = dmso_FC_data.merge(metas, how='outer', on='index')
    dmso_FC_table = dmso_FC_table[['index'] + metacolumnsTrans + genes]
    FC = FC.append(dmso_FC_table)

# because the gct files had non-uniform structures and metadata we'll now add 
# it back from a standardized and curated file. it contains columns: 
# id, replicates, x_dmso_pct for downstream use
ktoxmeta = pd.read_csv(infolder + 'meta.csv')


b = ['det_plate', 'det_well', 'pert_dose', 'pert_dose_unit',
     'pert_mfc_desc', 'pert_time', 'pert_type']


FC = FC[['index'] + b + genes]
FC = FC.merge(ktoxmeta, how='right', left_on='index', right_on='id')
FC = FC[['index'] + b + ['x_dmso_pct', 'replicates'] + genes]
FC.to_csv(outfolder + 'FC.csv', index=False)
