import math
def orderSplit(orders):
	splits = []
	remaining = 0
	for o in orders:
		split = 0
		orderSum = o
		if remaining != 0:
			split = split + 1
			if orderSum >= remaining:
				orderSum = orderSum - remaining
				remaining = 0
			else:
				remaining = remaining - orderSum
				orderSum = 0
		
		if remaining == 0 and orderSum != 0:
			split = split + math.ceil(orderSum/24.0)
			remaining = 24 - orderSum%24

		splits.append(split)

	for s in splits:
		print s


orderss = [10, 8, 5, 26]
orderSplit(orderss)