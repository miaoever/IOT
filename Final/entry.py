import k_means
import data_preprocess as dp
import boto3 as boto3
import os
import os.path
import sys

class mlEntry:
    bucket_name = 'iot-robotdata-noosa'
    feature_path = "features/"
    remote_data_path = "test/"
    local_data_path = "s3data/" # what's local path when executing on EMR?
    plot_path = "plot/"
    output_path = "output/"
    file_list = ["ws_orderinfo_orders_app.csv", "ws_orderinfo_orders_server.csv",\
                "ws_orderinfo_orderinround.csv", "ws_orderinfo_carinfo.csv",\
                "ws_orderinfo_demographic.csv"]
    
    data_processor = None

    def __init__(self):
        self.data_processor = dp.dataPreprocess(self.bucket_name, self.feature_path, self.remote_data_path, self.local_data_path, self.output_path+"pca/", self.plot_path, self.file_list)


    # use when order come in
    def startRegression(self):
        pass

    # use when order fulfilled
    def startCluster(self, sample_name):
        k_means.predict(self.bucket_name, self.feature_path, sample_name,self.output_path+"k-means/", self.plot_path)
    
    # use when order fulfilled
    def fulfillRegression(self):
        pass

    # pre-process -> trian kmeans -> train regression
    def startTrain(self):
        self.data_processor.start()
        self.upload_dir_s3(self.feature_path)
        self.upload_dir_s3(self.plot_path)
        self.upload_dir_s3(self.output_path)
        self.train_kmeans()

    def upload_dir_s3(self, dir):
        s3 = boto3.resource('s3')
        for file_name in os.listdir(dir):
            s3.meta.client.upload_file(dir+file_name, self.bucket_name, dir + file_name)

    def train_kmeans(self):
        k_means.train( self.bucket_name, self.feature_path,  "pca.csv", self.output_path+"k-means/", self.plot_path )

    def predict_kmeans(self, feature_name):
        k_means.predict( self.bucket_name, self.feature_path,  feature_name, self.output_path+"k-means/", self.plot_path )

if __name__ == "__main__":
    ml = mlEntry()

    # spark-submit entry.py 0 
    # spark-submit entry.py 1 sample-path sample-name # start prediction
    # spark-submit entry.py 2 sample-path sample-name # start cluster, update prediction
    if sys.argv[1]=='0':
        ml.startTrain()
    else if sys.argv[1]=='1':
        ml.startRegression()
    else:
        ml.startCluster()
        # ml.updateRegression()
