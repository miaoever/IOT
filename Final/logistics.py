import json
from os import path

import boto3
# import matplotlib.pyplot as plt
# import seaborn as sns
from pyspark.ml.classification import (LogisticRegression,
                                       LogisticRegressionModel)
from pyspark.ml.linalg import Vectors
from pyspark.sql import SparkSession
from pyspark.sql.functions import expr, lit


def read_data(bucket_name, feature_path, feature_name):
    """
    read from s3 csv and store to local
    """
    sc = SparkSession.builder.getOrCreate()
    data_path = path.join(feature_path, feature_name)
    if bucket_name:
        s3 = boto3.resource('s3')
        s3.Object(bucket_name, data_path).download_file(data_path)
    # read spark dataframe
    return sc.read.csv(data_path, inferSchema=True, header=True)

def avg_fulfill_time(df):
    # FIXME: the fulfill time is incorrect
    avg_fulfill = df.select('fulfillDuration').describe()
    return float(avg_fulfill.where("summary == 'mean'").first().fulfillDuration)

def transform_train_data(df):
    """
    Convert the data format to ['features', 'label'] for training
    Use Total amount of items, num of rounds, avg time of maintenance
    for each car as features
    """
    return df.rdd.map(
        lambda x: (
            Vectors.dense([x.amount, x.split, x.maintain4, x.maintain12]),
            x.intime
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
    # read spark dataframe
    df = read_data(bucket_name, feature_path, feature_name)

    # save the latest maintenance time
    save_maintain(df, output_path)

    # save average fulfilltime to json
    avg_time = avg_fulfill_time(df)
    with open(path.join(output_path, "avg_fulfill.json"), "w") as f:
        json.dump({ "avg_fulfill": avg_time }, f)

    df = df.withColumn(
        'intime',
        (df.fulfillDuration < avg_time).cast('integer')
    )
    train = transform_train_data(df)
    print "Generate training data:\n", train.take(3)

    lr = LogisticRegression(maxIter=10, regParam=0.3, elasticNetParam=0.8)
    # Fit the model
    lrModel = lr.fit(train)
    # save the model to output path
    model_path = path.join(output_path, "logistic-model")
    lrModel.write().overwrite().save(model_path)
    print "Write the logistic regression model to:", model_path
    # model summary
    train_pandas = lrModel.transform(train).toPandas()
    df_pandas = df.toPandas()
    df_pandas['predict'] = train_pandas['prediction']

    size = float(len(df_pandas))
    false_pos = (df_pandas['predict'] == 1) & (df_pandas['intime'] == 0)
    true_pos = (df_pandas['predict'] == 1) & (df_pandas['intime'] == 1)
    false_neg = (df_pandas['predict'] == 0) & (df_pandas['intime'] == 1)
    true_neg = (df_pandas['predict'] == 0) & (df_pandas['intime'] == 0)
    with open(path.join(output_path, "logistic-summary.json"), 'w') as f:
        json.dump({
            "True positive": float(true_pos.sum()) / size,
            "False positive": float(false_pos.sum()) / size,
            "True negative": float(true_neg.sum()) / size,
            "False negative": float(false_neg.sum()) / size,
            "coefficients": str(lrModel.coefficientMatrix)
        }, f)
    # plot the model
    # train_pandas = lrModel.transform(train).toPandas()
    # df_pandas = df.toPandas()
    # df_pandas['predict'] = train_pandas['prediction']
    # plt.scatter(x=df_pandas["amount"], y=df_pandas["split"])
    # img_path = path.join(plot_path, "logistic-regression.png")
    # plt.savefig(img_path)
    # print "Write model visualization to:", img_path

def predict(bucket_name, feature_path, feature_name, output_path, plot_path):
    model_path = path.join(output_path, "logistic-model")
    print "Load model from:", model_path
    lrModel = LogisticRegressionModel.load(model_path)

    # read last maintenance time from json
    maintain4 = 0.0
    maintain12 = 0.0
    with open(path.join(output_path, "last_maintain.json")) as f:
        last_maintain = json.load(f)
        maintain4 = last_maintain["maintain4"]
        maintain12 = last_maintain["maintain12"]

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
        path_or_buf=path.join(output_path, "classify-" + feature_name))

# For local test only
if __name__ == "__main__":
    train("", "./Final/features", "regression.csv", "./", "./")
    predict("", "./Final/features", "regression.csv", "./", "./")
