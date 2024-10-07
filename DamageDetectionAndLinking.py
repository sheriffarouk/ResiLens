# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 11:06:37 2024

@author: Sherif.Hamdy
"""

import pandas as pd
import glob
import logging
from pathlib import Path
from tqdm import tqdm

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize lists
scans = []
ResultsSeed = pd.DataFrame(columns=[
    'Scan', 'N. Seeds', 'Mean Seed Volume', 'STD Seed Volume', 'Mean Total Volume', 
    'Mean Damage Percent', 'Mean Seed Length', 'STD Seed Length', 'Mean Seed Thickness', 
    'STD Seed Thickness'
])

ResultsDamage = pd.DataFrame(columns=[
    'Mean Damage Volume', 'STD Damage Volume', 'Median Damage Volume', 'N Damages', 
    'Mean Damage Sphericity', 'DamageGreaterThan25', 'DamageGreaterThan50', 
    'DamageGreaterThan75', 'Damaged Seeds', 'Seeds With Important Damages', 'ERROR'
])

def removeOutliers(df, col, minq=0.0125, maxq=0.9875):
    """
    Removes outliers from a DataFrame based on quantiles.

    Parameters:
    df (DataFrame): The DataFrame to process.
    col (str): The column to check for outliers.
    minq (float): The lower quantile threshold.
    maxq (float): The upper quantile threshold.

    Returns:
    DataFrame: The filtered DataFrame with outliers removed.
    """
    if df.empty or col not in df.columns:
        return df  # Return unchanged DataFrame if invalid

    q_low = df[col].quantile(minq)
    q_hi = df[col].quantile(maxq)
    df_filtered = df[(df[col] < q_hi) & (df[col] > q_low)]

    return df_filtered

def damageBelongsToSeed(listOfDamage, listOfSeeds):
    """
    Determines whether damage belongs to seeds based on bounding box data.
    """
    damaged = 0
    matchingOx = [x for x in listOfDamage if "BoundingBoxOx" in x][0]
    matchingOy = [x for x in listOfDamage if "BoundingBoxOy" in x][0]
    matchingOz = [x for x in listOfDamage if "BoundingBoxOz" in x][0]
    
    matchingDx = [x for x in listOfDamage if "BoundingBoxDx" in x][0]
    matchingDy = [x for x in listOfDamage if "BoundingBoxDy" in x][0]
    matchingDz = [x for x in listOfDamage if "BoundingBoxDz" in x][0]

    for ss in range(len(listOfSeeds)):
        s = listOfSeeds.iloc[ss]
        for dd in range(len(listOfDamage)):
            d = listOfDamage.iloc[dd]

            if ((s[matchingOx] <= d[matchingOx]) and (s[matchingOy] <= d[matchingOy]) and
                (s[matchingOz] <= d[matchingOz]) and 
                (s[matchingDx] + s[matchingOx]) >= (0.75 * d[matchingDx] + d[matchingOx]) and
                (s[matchingDy] + s[matchingOy]) >= (0.75 * d[matchingDy] + d[matchingOy]) and
                (s[matchingDz] + s[matchingOz]) >= (0.75 * d[matchingDz] + d[matchingOz])):
                
                damaged += 1
                break
    return damaged

def process_seed_data(file):
    """
    Processes seed data from a given CSV file and removes outliers.
    """
    data = pd.read_csv(file, sep="\t", decimal=".")
    mykeys = data['seed.Label-Analysis'][0]
    mykeys2 = mykeys.split(',')
    myvalues = data['seed.Label-Analysis'][1:]
    
    tmp = myvalues.str.split(',', expand=True)
    sData = pd.DataFrame(tmp.values, columns=mykeys2).astype(float)
    
    matching = [s for s in sData if "Volume3d" in s][0]
    ssd = sData.loc[sData[matching] > 0.5]
    
    return removeOutliers(ssd, matching)

def process_damage_data(file, biggest_seed):
    """
    Processes damage data from a given CSV file and filters based on seed size.
    """
    data = pd.read_csv(file, sep="\t", decimal=".")
    mykeys = data['convex2.Label-Analysis'][0]
    mykeys2 = mykeys.split(',')
    myvalues = data['convex2.Label-Analysis'][1:]
    
    tmp = myvalues.str.split(',', expand=True)
    gData = pd.DataFrame(tmp.values, columns=mykeys2).astype(float)
    
    matchingDamage = [s for s in gData if "Volume3d" in s][0]
    DamageData = gData.loc[(gData[matchingDamage] > 0.25) & (gData[matchingDamage] <= biggest_seed)]
    
    return DamageData.sort_values(by=[matchingDamage])

# Path to CSV files
path = Path(r'C:/Directory/To/Image/Processing/Excel/Files')
allFiles = list(path.glob("*.csv"))

# Separate seed and damage data files
General = [s for s in allFiles if "_data_S" in str(s)]
Measure = [m for m in allFiles if "_data_D" in str(m)]

if len(General) == len(Measure):
    for count, file_ in tqdm(enumerate(Measure), total=len(Measure)):
        tempScanName = file_.name
        ScanName = tempScanName.split('.')[0]
        ScanNo, ScanNo2 = ScanName.split('_')[1:3]
        scans.append(f'SCAN_{ScanNo}_{ScanNo2}')
        
        # Process seed and damage data
        SeedData = process_seed_data(General[count])
        biggestSeed = SeedData['Volume3d'].iat[-1]
        DamageData = process_damage_data(file_, biggestSeed)
        
        # Calculate seed statistics
        SeedMeanVol = SeedData['Volume3d'].mean()
        ResultsSeed.at[count, 'Mean Seed Volume'] = SeedMeanVol
        ResultsSeed.at[count, 'STD Seed Volume'] = SeedData['Volume3d'].std()
        ResultsSeed.at[count, 'Mean Seed Length'] = SeedData['Length3d'].mean()
        ResultsSeed.at[count, 'STD Seed Length'] = SeedData['Length3d'].std()
        ResultsSeed.at[count, 'Mean Seed Thickness'] = SeedData['BoundingBoxDz'].mean()
        ResultsSeed.at[count, 'STD Seed Thickness'] = SeedData['BoundingBoxDz'].std()
        ResultsSeed.at[count, 'N. Seeds'] = SeedData['Volume3d'].count()

        # Calculate damage statistics
        ResultsDamage.at[count, 'N Damages'] = DamageData['Volume3d'].count()
        ResultsDamage.at[count, 'Mean Damage Volume'] = DamageData['Volume3d'].mean()
        ResultsDamage.at[count, 'Median Damage Volume'] = DamageData['Volume3d'].median()
        ResultsDamage.at[count, 'STD Damage Volume'] = DamageData['Volume3d'].std()

        # Important damage metrics
        TopDamageData = DamageData.loc[(DamageData['Volume3d'] > 1) & (DamageData['Volume3d'] <= biggestSeed)]
        ResultsDamage.at[count, 'N of Important Damages'] = TopDamageData['Volume3d'].count()
        ResultsDamage.at[count, 'Mean Volume of Important Damages'] = TopDamageData['Volume3d'].mean()
        ResultsDamage.at[count, 'STD Volume of Important Damages'] = TopDamageData['Volume3d'].std()
        ResultsDamage.at[count, 'Mean Damage Sphericity'] = DamageData['Sphericity'].mean()

        # Calculate damaged seeds
        DamagedSeeds = damageBelongsToSeed(DamageData, SeedData)
        TopDamagedSeeds = damageBelongsToSeed(TopDamageData, SeedData)
        ResultsDamage.at[count, 'Damaged Seeds'] = max(DamagedSeeds, TopDamagedSeeds)
        ResultsDamage.at[count, 'Seeds With Important Damages'] = min(DamagedSeeds, TopDamagedSeeds)

        # Error flag
        if 90 < SeedData['Volume3d'].count() < 110:
            ResultsDamage.at[count, 'ERROR'] = 0
        else:
            ResultsDamage.at[count, 'ERROR'] = 1

# Merge Results
R = pd.concat([ResultsSeed, ResultsDamage], axis=1).fillna(0)
R['Mean Total Volume'] = R['Mean Seed Volume'] + (R['Mean Damage Volume'] + R['Mean Volume of Important Damages']) / 2
R['Mean Damage Percent'] = 100 * (R['Mean Damage Volume'] + R['Mean Volume of Important Damages']) / (2 * R['Mean Total Volume'])
R['Scan'] = scans

# Save to Excel
R.to_excel(r'C:/OutputResultsDirectory/FileName.xlsx')
