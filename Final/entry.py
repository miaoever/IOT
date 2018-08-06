import k_means
import data_preprocess as dp
import boto3 as boto3
import os
import os.path
import sys
import time
import regression

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
    client = None

    def __init__(self):
        self.data_processor = dp.dataPreprocess(self.bucket_name, self.feature_path, self.remote_data_path,\
        self.local_data_path, self.output_path+"pca/", self.plot_path, self.file_list)
        self.client = boto3.client('s3')

    # use when order come in
    def orderIn(self, sample_path):
        f_list = self.wait_data(sample_path)
        # regression
        for f in f_list:
            self.data_processor.copy_to_feature(f)
            self.upload_dir_s3(self.feature_path)
            regression.predict(self.bucket_name,self.feature_path, f,self.output_path+"regression/", self.plot_path)

    # use when order fulfilled
    def orderFulfill(self, sample_path):
        f_list = self.wait_data(sample_path)
        for f in f_list:
            self.data_processor.pca_predict(f)
            self.upload_dir_s3(self.feature_path)
            k_means.predict(self.bucket_name, self.feature_path, f, self.output_path+"k-means/", self.plot_path)


    # pre-process -> trian kmeans -> train regression
    def startTrain(self):
        self.data_processor.start_train()
        self.upload_dir_s3(self.feature_path)
        self.upload_dir_s3(self.plot_path)
        regression.train(self.bucket_name, self.feature_path, "regression.csv", self.output_path+"regression/", self.plot_path)
        k_means.train( self.bucket_name, self.feature_path,  "pca.csv", self.output_path+"k-means/", self.plot_path )

    def wait_data(self, sample_path):
        self.client = boto3.client('s3')
        while True:
            response = self.client.list_objects(
                Bucket = self.bucket_name,
                Prefix = sample_path,
            )
            if response.has_key("Contents"):
                buffer_list = []
                for obj in response["Contents"]:
                    name = obj["Key"].split("/")[-1]
                    if not (name=="" or name==" "):
                        buffer_list.append(name)
                break

            print "Waiting for S3 buffer"
            time.sleep(1)

        self.data_processor.read_s3(buffer_list, sample_path)
        return buffer_list

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
    elif sys.argv[1]=='1':
        ml = mlEntry()
        ml.orderIn(sys.argv[2])
    else:
        ml = mlEntry()
        ml.orderFulfill(sys.argv[2])
