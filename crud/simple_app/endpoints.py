import logging
from flask_pymongo import pymongo
from flask import jsonify, request
import pandas as pd
import csv
import json
from pathlib import Path
from tkinter.tix import NoteBook
from unittest import result
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller 
from statsmodels.tsa.arima.model  import ARIMA 
from pandas.plotting import autocorrelation_plot
from pandas.tseries.offsets import DateOffset
from statsmodels.graphics.tsaplots import plot_acf,plot_pacf
import matplotlib.pyplot as plt
import statsmodels.api as sm
import cv2 
import os



con_string = "mongodb+srv://kanthavelu:kantha@cluster0.n5nxip0.mongodb.net"

client = pymongo.MongoClient(con_string)

db = client.get_database('demodatabase')

user_collection = pymongo.collection.Collection(db, 'democollection')
print("MongoDB connected Successfully")


def project_api_routes(endpoints):
    @endpoints.route('/hello', methods=['GET'])
    def hello():
        res = 'Hello world'
        print("Hello world")
        return res

    @endpoints.route('/register-user', methods=['POST'])
    def register_user():
        resp = {}
        try:
            req_body = request.json
            # req_body = req_body.to_dict()
            user_collection.insert_one(req_body)            
            print("User Data Stored Successfully in the Database.")
            status = {
                "statusCode":"200",
                "statusMessage":"User Data Stored Successfully in the Database."
            }
        except Exception as e:
            print(e)
            status = {
                "statusCode":"400",
                "statusMessage":str(e)
            }
        resp["status"] =status
        return resp


   

    @endpoints.route('/read-users',methods=['GET'])
    def read_users():
        resp = {}
        try:
            users = user_collection.find({})
            print(users)
            users = list(users)
            status = {
                "statusCode":"200",
                "statusMessage":"User Data Retrieved Successfully from the Database."
            }
            output = [{'Name' : user['name'], 'Email' : user['email']} for user in users]   #list comprehension
            resp['data'] = output
        except Exception as e:
            print(e)
            status = {
                "statusCode":"400",
                "statusMessage":str(e)
            }
        resp["status"] =status
        return resp

    @endpoints.route('/update-users',methods=['PUT'])
    def update_users():
        resp = {}
        try:
            req_body = request.json
            # req_body = req_body.to_dict()
            user_collection.update_one({"id":req_body['id']}, {"$set": req_body['updated_user_body']})
            print("User Data Updated Successfully in the Database.")
            status = {
                "statusCode":"200",
                "statusMessage":"User Data Updated Successfully in the Database."
            }
        except Exception as e:
            print(e)
            status = {
                "statusCode":"400",
                "statusMessage":str(e)
            }
        resp["status"] =status
        return resp    

    @endpoints.route('/delete',methods=['DELETE'])
    def delete():
        resp = {}
        try:
            delete_id = request.args.get('delete_id')
            user_collection.delete_one({"id":delete_id})
            status = {
                "statusCode":"200",
                "statusMessage":"User Data Deleted Successfully in the Database."
            }
        except Exception as e:
            print(e)
            status = {
                "statusCode":"400",
                "statusMessage":str(e)
            }
        resp["status"] =status
        return resp
    
    @endpoints.route('/file_upload',methods=['POST'])
    def file_upload():
        resp = {}
        try:
            req = request.form
            file = request.files.get('file')
            df = pd.read_csv(file)
            df.rename(columns = {df.columns[0]:'Month', df.columns[1]:'Sales'}, inplace = True)
            df.head()
            df.tail()
            df['Month']=pd.to_datetime(df['Month'])
            df.set_index('Month',inplace=True)
            def adfuller_test(sales):
               result=adfuller(sales)
               labels = ['ADF Test Statistic','p-value','#Lags Used','Number of Observations Used']
               for value,label in zip(result,labels):
                   print(label+' : '+str(value) )
               if result[1] <= 0.05:
                   print("strong evidence against the null hypothesis(Ho), reject the null hypothesis. Data has no unit root and is stationary")
               else:
                   print("weak evidence against null hypothesis, time series has a unit root, indicating it is non-stationary ")
            adfuller_test(df['Sales'])
            df['Sales First Difference'] = df['Sales'] - df['Sales'].shift(1)
            df['Sales'].shift(1)
            df['Seasonal First Difference']=df['Sales']-df['Sales'].shift(12)
            df.head(14)
            adfuller_test(df['Seasonal First Difference'].dropna())
            autocorrelation_plot(df['Sales'])
            model=ARIMA(df['Sales'],order=(1,1,1))
            model_fit=model.fit()
            model_fit.summary()
            df['forecast']=model_fit.predict(start=1,end=20,dynamic=True)
            
            model=sm.tsa.statespace.SARIMAX(df['Sales'],order=(1, 1, 1),seasonal_order=(1,1,1,12))
            results=model.fit()
           
            future_dates=[df.index[-1]+ DateOffset(months=x)for x in range(0,24)]
            future_datest_df=pd.DataFrame(index=future_dates[1:],columns=df.columns)
            future_df=pd.concat([df,future_datest_df])
            future_df['forecast'] = results.predict(start = 61, end = 70, dynamic= True)  
            future_df[['Sales', 'forecast']].plot(figsize=(15, 12))
            print(future_df[['Sales', 'forecast']])
            plt.plot()
            plt.savefig('plot.jpg')
            image = cv2.imread('plot.jpg')
            path = r"C:\Users\Kanthavelu\kantha\src\assets"
            (cv2.imwrite(os.path.join(path,'plot.jpg'), image))
          
            
            status = {
                "statusCode":"200",
                "statusMessage":"File uploaded Successfully."
            }
        except Exception as e:
            print(e)
            status = {
                "statusCode":"400",
                "statusMessage":str(e)
            }
        resp["status"] =status
        return resp


    return endpoints

