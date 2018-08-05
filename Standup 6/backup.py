import numpy as np
import csv

def readData(file):
    data = []
    peak = {'black':0,
            'blue':0,
            'green':0,
            'yellow':0,
            'red':0,
            'white':0}
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append([int(row['black']),int(row['blue']),int(row['green']),int(row['yellow']),int(row['red']),int(row['white'])])
            for color in peak:
                peak[color] = max(peak[color],int(row[color]))
    return np.array(data), [peak['black'],peak['blue'],peak['green'],peak['yellow'],peak['red'],peak['white']]


def learn(data, peak, N=24):
    best_count = {} #total usable
    best_s = {} #strategy
    for black in xrange(min(peak[0],N)+1):
        for blue in xrange(min(peak[1],N-black)+1):
            for green in xrange(min(peak[1],N-black-blue)+1):
                for yellow in xrange(min(peak[1],N-black-blue-green)+1):
                    for red in xrange(min(peak[1],N-black-blue-green-yellow)+1):
                        for white in xrange(min(peak[1],N-black-blue-green-yellow-red)+1):
                            n = black+blue+green+yellow+red+white
                            count = 0
                            for order in data:
                                count += min(black,order[0])+min(blue,order[1])+min(green,order[2])+min(yellow,order[3])+min(red,order[4])+min(white,order[5])
                                if (not n in best_count) or (best_count[n]<count):
                                    best_count[n]=count
                                    best_s[n]=[black,blue,green,yellow,red,white]
    for i in range(N+1):
        best_count[i]=best_count[i]/float(len(data))
    return best_count,best_s

def main():
    d, peak = readData('data/order1/ws_orderinfo_orders_server.csv')
    #print(peak)
    N = 24
    c,s = learn(d,peak,N)
    #print(c)
    #print(s)
    with open('result.csv', 'wb') as csvfile:
        fieldnames = ['total', 'black','blue','green','yellow','red','white','expected_usage']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(N+1):
            writer.writerow({'total': i, 'black':s[i][0],'blue':s[i][1],'green':s[i][2],'yellow':s[i][3],'red':s[i][4],'white':s[i][5],'expected_usage':c[i]})

main()
