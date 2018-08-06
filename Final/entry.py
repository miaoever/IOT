import os
import os.path
import sys
import time

import boto3 as boto3

import data_preprocess as dp
import k_means
import regression


class mlEntry:
    hadoop_home = "/home/hadoop/final/"
    bucket_name = 'iot-robotdata-noosa'
    feature_path = "/home/hadoop/final/features/"
    remote_data_path = "test/"
    local_data_path = "/home/hadoop/final/s3data/" # what's local path when executing on EMR?
    plot_path = "/home/hadoop/final/plot/"
    output_path = "/home/hadoop/final/output/"
    file_list = ["ws_orderinfo_orders_app.csv", "ws_orderinfo_orders_server.csv",\
                "ws_orderinfo_orderinround.csv", "ws_orderinfo_carinfo.csv",\
                "ws_orderinfo_demographic.csv"]

    data_processor = None
    client = None

    def __init__(self):
        self.data_processor = dp.dataPreprocess(self.feature_path, self.remote_data_path,\
        self.local_data_path, self.output_path+"pca/", self.plot_path, self.file_list)
        self.client = boto3.client('s3')

    # use when order come in
    def orderIn(self, stream_bucket, sample_path):
        f_list = self.wait_data(stream_bucket, sample_path)
        # regression
        for f in f_list:
            self.data_processor.copy_to_feature(f)
            self.upload_dir_s3(self.feature_path)
            regression.predict(self.bucket_name,self.feature_path, f,self.output_path+"regression/", self.plot_path)

        self.upload_dir_s3(self.output_path)

    # use when order fulfilled
    def orderFulfill(self, stream_bucket, sample_path):
        f_list = self.wait_data(stream_bucket, sample_path)
        for f in f_list:
            self.data_processor.pca_predict(f)
            self.upload_dir_s3(self.feature_path)
            k_means.predict(self.bucket_name, self.feature_path, f, self.output_path+"k-means/", self.plot_path)
        
        self.upload_dir_s3(self.output_path)


    # pre-process -> trian kmeans -> train regression
    def startTrain(self):
        self.data_processor.start_train(self.bucket_name)
        self.upload_dir_s3(self.feature_path)
        self.upload_dir_s3(self.plot_path)
        self.upload_dir_s3(self.output_path)
        regression.train(self.bucket_name, self.feature_path, "regression.csv", self.output_path+"regression/", self.plot_path)
        k_means.train( self.bucket_name, self.feature_path,  "pca.csv", self.output_path+"k-means/", self.plot_path )

    def wait_data(self, stream_bucket, sample_path):
        self.client = boto3.client('s3')
        while True:
            response = self.client.list_objects(
                Bucket = stream_bucket,
                Prefix = sample_path,
            )
            if response.has_key("Contents"):
                buffer_list = []
                for obj in response["Contents"]:
                    name = obj["Key"].split("/")[-1]
                    if not (name=="" or name==" "):
                        buffer_list.append(name)
                break

            print "Waiting for S3 buffer  "+stream_bucket + sample_path
            time.sleep(1)

        self.data_processor.read_s3(buffer_list, stream_bucket, sample_path)
        return buffer_list

    def upload_dir_s3(self, dir):
        s3 = boto3.resource('s3')
        for file in os.listdir(dir):
            path = dir_ + file_
            if os.path.isdir(path):
                self.upload_dir_s3(path+"/")
            else:
                s3.meta.client.upload_file(path, self.bucket_name, path.replace(self.hadoop_home, ""))

if __name__ == "__main__":
    # spark-submit entry.py 0  # train
    # spark-submit entry.py 1 sample-name # start prediction
    # spark-submit entry.py 2 sample-name # start cluster, update prediction
    if sys.argv[1]=='0':
        ml = mlEntry()
        ml.startTrain()
    elif sys.argv[1]=='1':
        ml = mlEntry()
        ml.orderIn(sys.argv[2],sys.argv[3]) # bucket name, prefix
    else:
        ml = mlEntry()
        ml.orderFulfill(sys.argv[2],sys.argv[3])
