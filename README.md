# Wiki Forecast:

- This repository contains the code for **"Wiki Forecast Project"**.
- The objective of this project is to forecast web traffic for individual Wikipedia pages reliably to enhance content management efforts.
  
## Introduction:
- In the digital age, understanding and predicting web traffic patterns is paramount for effective content management, resource allocation, and strategic decision-making. With the exponential growth of online platforms like Wikipedia, accurately forecasting web traffic has become increasingly challenging yet crucial. 
- We aim to construct a web traffic forecasting system by crafting a LSTM model using the `neuralforecast` library. This model will analyze the time series data of each Wikipedia page to forecast the daily visits throughout the prediction period.
- In this project we have used the **Web Traffic Time Series Forecasting** dataset from Kaggle to train our model. 

## 📝 Description of files:

- __data/:__ This directory contains subdirectories for raw and processed data. Raw data files (train.tsv and test.tsv) are stored in the raw/ subdirectory, while processed data files (train.csv and test.csv) are stored in the processed/ subdirectory. Intermediate data files generated during data preprocessing can be stored in the interim/ subdirectory if necessary.

- __notebooks/:__ Jupyter notebooks for exploratory data analysis, data preprocessing, model development, and evaluation are stored in this directory.

- __README.md:__ Documentation providing an overview of the project, instructions for setup and usage, and any additional information relevant to users and contributors.

## :hammer_and_wrench: Requirements
* Python 3.5+
* pandas
* matplotlib
* scikit-learn
* streamlit
* neuralforecast
* pytorch

## Contributors <img src="https://raw.githubusercontent.com/TheDudeThatCode/TheDudeThatCode/master/Assets/Developer.gif" width=35 height=25> 
-	Mehul Jain 
-	Bishal Agrawal 
-	Ajay Karthick Senthil Kumar



