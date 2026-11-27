def single_number(nums):
    hashmap ={}
    for num in nums:
        hashmap[num]= hashmap.get(num,0)+1
    for num, cnt in hashmap.items():
        if cnt ==1:
            return num
    return -1