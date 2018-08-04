import data_preprocess as dp
import boto3 as boto3
import os
import os.path

class mlEntry:
    bucket_name = 'iot-robotdata-noosa'
    feature_path = "features/"
    remote_path = "test/"
    local_path = "s3data/" # what's local path when executing on EMR?
    plot_path = "plot/"
    file_list = ["ws_orderinfo_orders_app.csv", "ws_orderinfo_orders_server.csv",\
                "ws_orderinfo_orderinround.csv", "ws_orderinfo_carinfo.csv",\
                "ws_orderinfo_demographic.csv"]
    
    data_processor = None

    def __init__(self):
        self.data_processor = dp.dataPreprocess(self.bucket_name, self.feature_path, self.remote_path, self.local_path, self.plot_path, self.file_list)

    def startUpdate(self):
        self.data_processor.start()

    def upload_dir_s3(self, dir):
        s3 = boto3.resource('s3')
        for file_name in os.listdir(dir):
            s3.meta.client.upload_file(dir+file_name, self.bucket_name, dir + file_name)


if __name__ == "__main__":
    ml = mlEntry()
    ml.startUpdate()
    ml.upload_dir_s3(ml.feature_path)
    ml.upload_dir_s3(ml.plot_path)