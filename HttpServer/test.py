import csv

def read_back_up_strategy():
    strats = {}
    with open('../Final/result.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            strats[int(row['total'])] = [int(row['black']),int(row['blue']),int(row['green']),int(row['yellow']),int(row['red']),int(row['white'])]
    return strats