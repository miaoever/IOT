import boto3 as boto3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import visuals as vs
import pickle

class dataPreprocess:
    df_server = None
    df_app = None
    df_car = None
    df_user = None
    df_user_server = None
    df_round = None

    bucket_name = ''
    feature_path = ''
    output_path = ''
    remote_path = ''
    local_path = ''
    plot_path = ''
    file_list = []


    pca = None
    pca_result = None
    pca_summary = None

    def __init__(self, bucket_name, feature_path, remote_path, local_path, output_path, plot_path, file_list):
        self.bucket_name = bucket_name
        self.feature_path = feature_path
        self.remote_path = remote_path
        self.local_path = local_path
        self.output_path = output_path
        self.plot_path = plot_path
        self.file_list = file_list

    def read_s3(self, list, path):
        for name in list:
            if name=='':
                continue
            file_name = path + name
            local_file_name = self.local_path + name
            s3 = boto3.resource('s3')
            s3.Object(self.bucket_name, file_name).download_file(local_file_name)

        obj = []
        for name in list:
            file_name = path + name
            obj.append({"Key":file_name})

        bucket = s3.Bucket(self.bucket_name)
        bucket.delete_objects(Delete = {
            "Objects" : obj
        })


    def generate_train_df(self):
        self.df_app = pd.read_csv(self.local_path+'ws_orderinfo_orders_app.csv', header=0)
        self.df_server = pd.read_csv(self.local_path+'ws_orderinfo_orders_server.csv', header=0)
        self.df_round = pd.read_csv(self.local_path+'ws_orderinfo_orderinround.csv', header=0)
        self.df_car = pd.read_csv(self.local_path+'ws_orderinfo_carinfo.csv', header=0)

    def cal_server(self):
        self.df_server = self.df_server.dropna()
        self.df_server["orderdate"] = self.df_server["orderdate"].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
        self.df_server["tokendate"] = self.df_server["tokendate"].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
        self.df_server["shipdate"] = self.df_server["shipdate"].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))

        self.df_server["transitDuration"] = (self.df_server["shipdate"]-self.df_server["tokendate"])/ np.timedelta64(1, 's')
        self.df_server["fulfillDuration"] = (self.df_server["shipdate"]-self.df_server["orderdate"])/ np.timedelta64(1, 's')

        self.df_server["amount"] = self.df_server["red"]+self.df_server["blue"]+self.df_server["yellow"]+self.df_server["black"]+self.df_server["white"]

    def combine_user_server(self):
        dic = {}

        # Combine with customer info
        self.df_user = pd.read_csv(self.local_path+'ws_orderinfo_demographic.csv', header=0)
        self.df_user_server = pd.merge(self.df_server, self.df_user, how='inner', left_on="customer", right_on="name")
        self.df_user_server = self.df_user_server.drop(columns=['name','orderdate','tokendate','shipdate', 'id','entryid'])
        for key in ["customer","age", "sex", "city", "state", "country",\
                        "income", "credit","education", "occupation"]:
            dic[key] = {}
            ## Add Customer ID (Integer number)
            id = 1
            for _,name in self.df_user_server[[key]].drop_duplicates()[key].iteritems():
                dic[key][name] = id # id starts from 0
                id = id+1
            self.df_user_server[key] = self.df_user_server[key].apply(lambda x: dic[key][x])

            
        print "dictionary keys:",dic.keys()

        f = open(self.output_path+"user.dict", 'w')
        pickle.dump(dic, f)
        f.close()

        print self.df_user_server.info()

    def pca(self):
        index = ["sex", "age", "state", "education",\
                "transitDuration","fulfillDuration", \
                "green","blue","black","yellow","red","white","amount"]

        scaler = StandardScaler()

        self.pca_result = scaler.fit_transform(self.df_user_server[index].values)

        self.pca = PCA(n_components=2)
        self.pca_result= self.pca.fit_transform(self.pca_result)

        self.pca_summary = vs.pca_results(self.df_user_server[index], self.pca, self.plot_path)
        
        f = open(self.output_path+"pca.model", 'w')
        pickle.dump(self.pca, f)
        f.close()
        f = open(self.output_path+"pca_summary.csv", 'w')
        pickle.dump(self.pca_summary, f)
        f.close()

        np.savetxt(self.feature_path + "pca.csv", self.pca_result, delimiter=",", header="pca1,pca2", comments='')




    def regression(self):
        countSplit = [];  # countSplit[0]: number of being split of order 1

        for k in xrange(1, len(self.df_server)+1):
            cluster = [i for i in xrange(len(self.df_round)) if self.df_round["orderid"][i]==k]
            countSplit.append(len(cluster))
            
        self.df_server["split"] = self.df_server["id"].apply(lambda id: countSplit[id-1])

        self.df_car["entermaintence"] = self.df_car["entermaintence"].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
        self.df_car["exitmaintence"] = self.df_car["exitmaintence"].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
        self.df_car["maintainDuration"] = (self.df_car["exitmaintence"]-self.df_car["entermaintence"])/ np.timedelta64(1, 's')
        self.df_car = self.df_car[["roundid","maintainDuration"]]
        self.df_app = pd.merge(self.df_app, self.df_car, how='left', left_on="id", right_on="roundid")

        self.df_app.fillna(0)
        self.df_app.fillna(0)

        self.df_app_4= self.df_app.iloc[[i for i in xrange(len(self.df_app)) if self.df_app["carid"][i]==4]][["id","maintainDuration"]]
        self.df_app_12= self.df_app.iloc[[i for i in xrange(len(self.df_app)) if self.df_app["carid"][i]==12]][["id","maintainDuration"]]
        # self.df_app = self.df_app[["id","maintainDuration"]]
        self.df_round = pd.merge(self.df_round, self.df_app[["id","carid"]], how='left', left_on="roundid", right_on="id", suffixes = ["",""])
        self.df_round = self.df_round[["roundid","orderid","carid"]]

        time = 0
        count = 1
        for index, row in self.df_app_4.iterrows():
            if np.isnan(row["maintainDuration"]):
                self.df_app_4["maintainDuration"][index] = time / count
            else:
                time = time + row["maintainDuration"]
                self.df_app_4["maintainDuration"][index] = time / count
                count = count+1
                
            self.df_app["maintainDuration"][int(row["id"]-1)] = self.df_app_4["maintainDuration"][index]
            
        time = 0
        count = 1
        for index, row in self.df_app_12.iterrows():
            if np.isnan(row["maintainDuration"]):
                self.df_app_12["maintainDuration"][index] = time / count
            else:
                time = time + row["maintainDuration"]
                self.df_app_12["maintainDuration"][index] = time / count
                count = count+1
                
            self.df_app["maintainDuration"][int(row["id"]-1)] = self.df_app_12["maintainDuration"][index]

        self.df_server["maintain4"] = 0.0
        self.df_server["maintain12"] = 0.0

        order2round = {}

        for i in xrange(len(self.df_round)):
            if not order2round.has_key(int(self.df_round["orderid"][i])-1):
                order2round[int(self.df_round["orderid"][i])-1] = []
                
            order2round[int(self.df_round["orderid"][i])-1].append(int(self.df_round["roundid"][i])-1)
            
        for i in xrange(len(self.df_server)):
            if not order2round.has_key(self.df_server["id"][i]):
                continue
            rounds = order2round[self.df_server["id"][i]]
            for r in rounds:
                if self.df_app["carid"][r]==4:
                    self.df_server["maintain4"][i] =  self.df_app["maintainDuration"][r]
                else:
                    self.df_server["maintain12"][i] =  self.df_app["maintainDuration"][r]
                    
        self.df_server.to_csv(path_or_buf = self.feature_path + "regression.csv")

    def pca_predict(self, sample_name):
        index = ["sex", "age", "state", "education",\
        "transitDuration","fulfillDuration", \
        "green","blue","black","yellow","red","white","amount"]
        self.df_user_server = pd.read_csv(self.local_path + sample_name, \
            names = ["orderid","age","sex","state","education","transitDuration","fulfillDuration","black","blue","green","yellow","red","white","amount"])        
        self.df_user_server.drop(columns=['orderid'])
        self.df_user_server = self.df_user_server[index]
        f = open(self.output_path+"user.dict", 'r')
        dic = pickle.load(f)
        f.close()
        self.df_user_server["sex"] = self.df_user_server["sex"].apply(lambda x: dic["sex"][x])
        self.df_user_server["state"] = self.df_user_server["state"].apply(lambda x: dic["state"][x])
        self.df_user_server["education"] = self.df_user_server["education"].apply(lambda x: dic["education"][x])
        
        f = open(self.output_path+"pca.model", 'r')
        self.pca = pickle.load(f)
        f.close()

        scaler = StandardScaler()
        self.pca_result = scaler.fit_transform(self.df_user_server.values)
        self.pca_result = self.pca.transform(self.pca_result)
        print self.pca_result
        self.pca_summary = vs.pca_results(self.df_user_server, self.pca, self.plot_path)

        np.savetxt(self.feature_path + sample_name, self.pca_result, delimiter=",", header="pca1,pca2", comments='')

    def copy_to_feature(self, sample_name):
        self.df = pd.read_csv(self.local_path + sample_name,\
                names = ["orderid","black","blue","green","yellow","red","white","amount","split"])
        self.df.to_csv(path_or_buf = self.feature_path + sample_name)

    def start_train(self):
        self.read_s3(self.file_list, self.remote_path)
        self.generate_train_df()
        self.cal_server()
        self.combine_user_server()
        self.pca()
        self.regression()
