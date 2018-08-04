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
    sample_file = ""
    
    data_processor = None

    def __init__(self):
        self.data_processor = dp.dataPreprocess(self.bucket_name, self.feature_path, self.remote_data_path,\
         self.local_data_path, self.output_path+"pca/", self.plot_path, self.file_list, self.sample_file)


    # use when order come in
    def orderIn(self, sample_name):
        self.data_processor.pca_predict()
        # regression

    # use when order fulfilled
    def orderFulfill(self, sample_name):
        k_means.predict(self.bucket_name, self.feature_path, sample_name,self.output_path+"k-means/", self.plot_path)
        # HCA cluster
        # update regression table


    # pre-process -> trian kmeans -> train regression
    def startTrain(self):
        self.data_processor.start_train()
        self.upload_dir_s3(self.feature_path)
        self.upload_dir_s3(self.plot_path)
        self.upload_dir_s3(self.output_path)
        k_means.train( self.bucket_name, self.feature_path,  "pca.csv", self.output_path+"k-means/", self.plot_path )

    def upload_dir_s3(self, dir):
        s3 = boto3.resource('s3')
        for file_name in os.listdir(dir):
            s3.meta.client.upload_file(dir+file_name, self.bucket_name, dir + file_name)

if __name__ == "__main__":
    # spark-submit entry.py 0  # train
    # spark-submit entry.py 1 sample-name # start prediction
    # spark-submit entry.py 2 sample-name # start cluster, update prediction
    if sys.argv[1]=='0':
        ml = mlEntry()
        ml.startTrain()
    else if sys.argv[1]=='1':
        ml = mlEntry()
        ml.orderIn(sys.argv[2])
    else:
        ml = mlEntry()
        ml.orderFulfill(sys.argv[2])
