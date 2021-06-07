import pathlib
import sys

import pandas as pd

def prepare_reports():
    folder_path = str(pathlib.Path().absolute())
    netact_report_cols = ['Source LNCEL name', 'eci_id', 'Intra eNB neighbor HO: Att', 'Inter eNB neighbor HO: Att']
    netact_report = pd.read_csv(r"C:\Users\wkebbab\Desktop\RSLTE031_-_Neighbor_HO_walid.csv", delimiter=";",
                                usecols=netact_report_cols)

    oss_report_cols = ['name', 'eutraCelId']
    oss_report = pd.read_csv(folder_path + "\export_20210506.csv", encoding='utf8', delimiter="\t",
                             usecols=oss_report_cols)

    netact_report.rename(columns={"eci_id": "eutraCelId"}, inplace=True)

    merged_reports = netact_report.merge(oss_report, on="eutraCelId")
    merged_reports.rename(columns={"name": "Target name"}, inplace=True)

    merged_reports['Total eNB neighbor HO: Att'] = merged_reports['Intra eNB neighbor HO: Att'] + merged_reports[
        'Inter eNB neighbor HO: Att']

    merged_reports.drop([merged_reports.columns[1], merged_reports.columns[2], merged_reports.columns[3]], axis=1,inplace=True)
    merged_reports = merged_reports[merged_reports['Total eNB neighbor HO: Att'] > 200]
    merged_reports = merged_reports[merged_reports['Source LNCEL name'].astype(str).str[:-3] != merged_reports['Target name'].astype(str).str[:-3]]
    merged_reports=merged_reports.groupby(['Source LNCEL name', 'Target name'])['Total eNB neighbor HO: Att'].sum()
    merged_reports.to_csv(folder_path + "\merged_reports.csv", sep=';')
    merged_reports = pd.read_csv(folder_path + "\merged_reports.csv",delimiter=";")
    cells_st=merged_reports['Source LNCEL name'].unique()
    cells_st = pd.DataFrame(cells_st,columns=['Source LNCEL name']).sort_values(by=['Source LNCEL name'])
    cells_st = cells_st[cells_st['Source LNCEL name'].apply(lambda x : len(x)==12)]
    cells_st.to_csv(folder_path+"\cells_st.csv",sep=";")
