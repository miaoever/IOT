import numpy as np
import csv
import matplotlib.pyplot as plt
from sklearn import manifold
import time as time
from sklearn.cluster import AgglomerativeClustering
from sklearn import preprocessing
from scipy import ndimage
import mpl_toolkits.mplot3d.axes3d as p3
import seaborn as sns
from scipy.spatial import distance_matrix
from scipy.cluster.hierarchy import dendrogram, linkage


def process_data(path):
    mydata = []
    with open(path) as f:
        head = True
        reader = csv.reader(f,delimiter=',')
        for row in reader:
            if head:
                head = False
            elif int(row[-2])>0:
                mydata.append([float(row[6]),float(row[7]),float(row[-1])/int(row[-2])])
    return mydata



def showdata(X):
    # #############################################################################
    # Compute clustering
    print("Compute unstructured hierarchical clustering...")
    
    st = time.time()
    ward = AgglomerativeClustering(n_clusters=6, linkage='ward').fit(X)
    elapsed_time = time.time() - st
    label = ward.labels_
    print("Elapsed time: %.2fs" % elapsed_time)
    print("Number of points: %i" % label.size)
    
    # #############################################################################
    # Plot result
    fig = plt.figure()
    ax = p3.Axes3D(fig)
    ax.view_init(7, -80)
    for l in np.unique(label):
        ax.scatter(X[label == l, 0], X[label == l, 1], X[label == l, 2],
                   color=plt.cm.jet(np.float(l) / np.max(label + 1)),
                   s=20, edgecolor='k')
    plt.title('Without connectivity constraints (time %.2fs)' % elapsed_time)
    
    # #############################################################################
    # Define the structure A of the data. Here a 10 nearest neighbors
    from sklearn.neighbors import kneighbors_graph
    connectivity = kneighbors_graph(X, n_neighbors=10, include_self=False)
    
    # #############################################################################
    # Compute clustering
    print("Compute structured hierarchical clustering...")
    st = time.time()
    ward = AgglomerativeClustering(n_clusters=6, connectivity=connectivity,
                                   linkage='ward').fit(X)
    elapsed_time = time.time() - st
    label = ward.labels_
    print("Elapsed time: %.2fs" % elapsed_time)
    print("Number of points: %i" % label.size)
    
    # #############################################################################
    # Plot result
    fig = plt.figure()
    ax = p3.Axes3D(fig)
    ax.view_init(7, -80)
    for l in np.unique(label):
        ax.scatter(X[label == l, 0], X[label == l, 1], X[label == l, 2],
                   color=plt.cm.jet(float(l) / np.max(label + 1)),
                   s=20, edgecolor='k')
    plt.title('With connectivity constraints (time %.2fs)' % elapsed_time)
    
    plt.show()

def hca(X):
 #   path = sys.argv[1]
    #path = 'data/orderWithCustomer.csv'
    #X, y = read_csv(path)

    # find distance matrix
    d = distance_matrix(X, X)
    for link in ('ward', 'average', 'complete'):
        clustering = AgglomerativeClustering(linkage=link, n_clusters=10).fit(d)
        st = time.time()
        label = clustering.labels_
        elapsed_time = time.time() - st

    # Draw the clustering heatmap based on different methods
    sns.set(color_codes=True)
    g1 = sns.clustermap(X, method='ward', metric='euclidean', figsize=(5, 8))
    g2 = sns.clustermap(X, method='average', metric='euclidean', figsize=(5, 8))
    g3 = sns.clustermap(X, method='complete', metric='euclidean', figsize=(5, 8))

    # Draw the dendrogram of the clustering based on different methods
    plt.figure()
    plt.title('Hierarchical Clustering Dendrogram (ward)')
    plt.xlabel('sample index')
    plt.ylabel('distance')
    Z = linkage(X, 'ward')
    dendrogram(
        Z,
        leaf_rotation=90.,
        leaf_font_size=8.,
    )
    plt.figure()
    plt.title('Hierarchical Clustering Dendrogram (average)')
    plt.xlabel('sample index')
    plt.ylabel('distance')
    Z = linkage(X, 'average')
    dendrogram(
        Z,
        leaf_rotation=90.,
        leaf_font_size=8.,
    )
    plt.figure()
    plt.title('Hierarchical Clustering Dendrogram (complete)')
    plt.xlabel('sample index')
    plt.ylabel('distance')
    Z = linkage(X, 'complete')
    dendrogram(
        Z,
        leaf_rotation=90.,
        leaf_font_size=8.,
    )
    plt.show()



X = np.array(process_data("data/orderWithCustomer.csv"))
X_scaled = preprocessing.scale(X)
print("--------------raw data----------------")
showdata(X)
hca(X)
print("--------------scaled data----------------")
showdata(X_scaled)
hca(X_scaled)