import boto3 as boto3
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext
from pyspark.sql import DataFrameReader
from pyspark import SparkContext, HiveContext
from pyspark.ml.clustering import KMeans
from pyspark.ml.clustering import KMeansModel
from pyspark.ml.linalg import Vectors
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.feature import StandardScaler
import matplotlib.pyplot as plt

import numpy as np
from numpy import array
from math import sqrt


def train( bucket_name, feature_path, feature_name, output_path, plot_path ):
    sc = SparkContext.getOrCreate()
    sqlCtx = SQLContext(sc)

    # read from s3 csv and store to local
    path = feature_path + feature_name # used both locally and remotely: features/pca.csv
    s3 = boto3.resource('s3')
    s3.Object(bucket_name, path).download_file(path)
    df_spark = sqlCtx.read.csv(path, header=True, inferSchema=True)

    # Dataframe to rdd
    vecAssembler = VectorAssembler(inputCols=df_spark.columns, outputCol="features")
    df_spark = vecAssembler.transform(df_spark)
    rdd = df_spark.rdd.map(lambda x: array(x["features"]))
    print rdd.take(10)
    # From here: K-means specific
    # Pick k
    cost = np.zeros(20)
    for k in range(2,20):
        kmeans = KMeans().setK(k).setSeed(1).setFeaturesCol("features")
        model = kmeans.fit(df_spark.sample(False,0.5, seed=42))
        cost[k] = model.computeCost(df_spark) 
    plt.figure(1)
    fig, ax = plt.subplots(1,1, figsize =(8,6))
    ax.plot(range(2,20),cost[2:20])
    ax.set_xlabel('k')
    ax.set_ylabel('cost')
    plt.savefig( plot_path + "k-means vary-k.png" )

    # Train and upload model to s3
    k = 8
    kmeans = KMeans().setK(k).setSeed(1).setFeaturesCol("features")
    model = kmeans.fit(df_spark)
    
    model.write().overwrite().save(output_path + "k-means.model") # save the model to s3

    data = model.transform(df_spark).toPandas()
    print data.info()
    data.to_csv(output_path+"/transformed.csv")
    # #Plotting
    fig = plt.figure(2, figsize=(5,5))
    plt.scatter(data["pca1"], data["pca2"], c=data["prediction"], s=30, cmap='viridis')
    plt.title("K Means (K=%d)"%k, fontsize=14)    
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.savefig( plot_path + "k-means-cluster.png" )


def predict( bucket_name, feature_path, feature_name, output_path, plot_path ):
    sc = SparkContext.getOrCreate()
    sqlCtx = SQLContext(sc)

    # load existing model
    model_path = output_path + "k-means.model"
    model = KMeansModel.load(model_path)

    # read from s3 csv and store to local
    path = feature_path + feature_name # used both locally and remotely: features/pca.csv
    s3 = boto3.resource('s3')
    s3.Object(bucket_name, path).download_file(path)
    df_spark = sqlCtx.read.csv(path, header=True, inferSchema=True)

    # Dataframe to rdd
    vecAssembler = VectorAssembler(inputCols=df_spark.columns, outputCol="features")
    df_spark = vecAssembler.transform(df_spark)
    rdd = df_spark.rdd.map(lambda x: array(x["features"]))
    print rdd.take(10)

    # From here: K-means model use for prediction

    data = model.transform(df_spark).toPandas()
    print output_path + "pred-"+feature_name
    data.to_csv(path_or_buf= (output_path + "pred-"+feature_name))