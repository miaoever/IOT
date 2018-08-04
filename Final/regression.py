import boto3
from pyspark.sql import SparkSession
from pyspark.ml.regression import LinearRegression, LinearRegressionModel
from pyspark.ml.linalg import Vectors
import matplotlib.pyplot as plt
import seaborn as sns
from os import path

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

def transform_train_data(df):
    """
    Convert the data format to ['features', 'label'] for training
    Use Total amount of items, num of rounds, avg time of maintenance
    for each car as features
    """
    return df.rdd.map(
        lambda x: (
            Vectors.dense([x.amount, x.split, x.maintain4, x.maintain12]),
            x.transitDuration
        )
    ).toDF(["features", "label"])

def train(bucket_name, feature_path, feature_name, output_path, plot_path):
    # read spark dataframe
    df = read_data(bucket_name, feature_path, feature_name)

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
    sns.pairplot(
        df_pandas,
        x_vars=['amount', 'split', 'maintain4', 'maintain12'],
        y_vars='predict', kind='reg'
    )
    img_path = path.join(plot_path, "linear-regression.png")
    plt.savefig(img_path)
    print "Write model visualization to:", img_path

def predict(bucket_name, feature_path, feature_name, output_path, plot_path):
    model_path = path.join(output_path, "regression-model")
    print "Load model from:", model_path
    lrModel = LinearRegressionModel.load(model_path)

    # read data from s3 for prediction
    df = read_data(bucket_name, feature_path, feature_name)
    test = transform_train_data(df)

    lrModel.transform(test).toPandas().to_csv(
        path_or_buf=path.join(output_path, "pred-" + feature_name))

# For local test only
if __name__ == "__main__":
    train("", "./Final/features", "regression.csv", "./", "./")
    predict("", "./Final/features", "regression.csv", "./", "./")
