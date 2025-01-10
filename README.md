**Project Title**

ResiLens

**Description**

A research project aiming to identify bruchid resistance sources in lentil 

**Getting Started**

Dependencies
    
    Windows 10
    AVIZO
    Python
    libraries: pandas, glob,logging, pathlib, tqdm

**Installing**

 1. Feature Extraction

    The script files FeaturesExtraction.scro and FeaturesExtraction.scro should be installed inside script folder of avizo program for example "C:/Program Files/Avizo-9.0.1/share/script-objects/".
    
    After loading the tomographic image in AVIZO, the processing module can be found by:
  
    1.1- Right-click on the image
    
    1.2- Select FeaturesExtraction
    
    1.3- Click on start processing

  3. Damage Detection And Linking    

     The input of the file "DamageDetectionAndLinking.py" should be modified before running to path to CSV files extracted from the previous modules.
