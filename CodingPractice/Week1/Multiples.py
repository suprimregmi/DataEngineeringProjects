# a =[]
# for i in range(1,1001):
# 	if i%3==0 or i%5==0:
# 		a.append(i)
		
# print(sum(a))


# 1 liner

print(sum(i for i in range(1, 1000) if i % 3 == 0 or i % 5 == 0))