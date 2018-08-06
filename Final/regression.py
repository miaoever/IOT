import json
from os import path

import boto3
import matplotlib.pyplot as plt
import seaborn as sns
from pyspark.ml.linalg import Vectors
from pyspark.ml.regression import LinearRegression, LinearRegressionModel
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
from pyspark import SparkContext, HiveContext
from pyspark.sql import SQLContext


def read_data(bucket_name, feature_path, feature_name):
    """
    read from s3 csv and store to local
    """
    print feature_name
    print feature_path
    sc = SparkSession.builder.getOrCreate()
    data_path = path.join(feature_path, feature_name)
    if bucket_name:
        s3 = boto3.resource('s3')
        s3.Object(bucket_name, data_path).download_file(data_path)
    # read spark dataframe
    return sc.read.csv(data_path, inferSchema=True, header=True)

def transform_train_data(df):
    """
    Convert the data format to ['features', 'label'] for training
    Use Total amount of items, num of rounds, avg time of maintenance
    for each car as features
    """
    return df.rdd.map(
        lambda x: (
            Vectors.dense([x.amount, x.split, x.maintain4, x.maintain12]),
            # FIXME: fulfill duration is not correct right now
            x.fulfillDuration
        )
    ).toDF(["features", "label"])

def save_maintain(df, output_path):
    df = df.where((df.maintain4 != 0.0) & (df.maintain12 != 0.0))
    last_maintain = df.select("maintain4", "maintain12").collect()[-1]
    with open(path.join(output_path, "last_maintain.json"), 'w') as f:
        json.dump({
            "maintain4": last_maintain.maintain4,
            "maintain12": last_maintain.maintain12
        }, f)

def train(bucket_name, feature_path, feature_name, output_path, plot_path):
    sc = SparkContext.getOrCreate()
    sqlCtx = SQLContext(sc)

    # read spark dataframe
    df = read_data(bucket_name, feature_path, feature_name)

    # save the latest maintenance time
    save_maintain(df, output_path)

    train = transform_train_data(df)
    print "Generate training data:\n", train.take(3)

    lr = LinearRegression(maxIter=10, regParam=0.3, elasticNetParam=0.8)
    # Fit the model
    lrModel = lr.fit(train)
    # save the model to output path
    model_path = path.join(output_path, "regression-model")
    lrModel.write().overwrite().save(model_path)
    print "Write the linear regression model to:", model_path
    # plot the model
    train_pandas = lrModel.transform(train).toPandas()
    df_pandas = df.toPandas()
    df_pandas['predict'] = train_pandas['prediction']
    fig = plt.figure(3)
    sns.pairplot(
        df_pandas,
        x_vars=['amount', 'split', 'maintain4', 'maintain12'],
        y_vars='predict', kind='reg'
    )
    img_path = path.join(plot_path, "linear-regression.png")
    plt.savefig(img_path)
    print "Write model visualization to:", img_path

def predict(bucket_name, feature_path, feature_name, output_path, plot_path):    
    sc = SparkContext.getOrCreate()
    sqlCtx = SQLContext(sc)

    model_path = path.join(output_path, "regression-model")
    print "Load model from:", model_path
    lrModel = LinearRegressionModel.load(model_path)

    # read last maintenance time from json
    maintain4 = 0.0
    maintain12 = 0.0
    with open(path.join(output_path, "last_maintain.json")) as f:
        last_maintain = json.load(f)
        maintain4 = last_maintain['maintain4']
        maintain12 = last_maintain['maintain12']

    # read data from s3 for prediction
    df = read_data(bucket_name, feature_path, feature_name)
    # transform predict data
    df = df.withColumn('maintain4', lit(maintain4))
    df = df.withColumn('maintain12', lit(maintain12))
    test = df.rdd.map(
        lambda x: (
            Vectors.dense([x.amount, x.split, x.maintain4, x.maintain12]),
        )
    ).toDF(["features"])

    lrModel.transform(test).toPandas().to_csv(
        path_or_buf=path.join(output_path, "pred-" + feature_name))

# For local test only
if __name__ == "__main__":
    train("", "./Final/features", "regression.csv", "./", "./")
    predict("", "./Final/features", "regression.csv", "./", "./")
