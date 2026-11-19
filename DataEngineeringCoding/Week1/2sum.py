print(" Solving 2 sum")
# given set of numbers and a target number, find two numbers in the set that add up to the target number
# def fun takes array and target
# define hash set {} IF I,J IN ENUMERTE IN NUMS IF TARGET-J IN HASH CHA VANE --> RETRUN SET =NUM[I] ELSE SET =SET(I})   


def two_sum(nums, target):
    num_dict = {}

    for i, num in enumerate(nums):
        complement = target - num

        if complement in num_dict:
            return [num_dict[complement], i]

        num_dict[num] = i

    return None


result = two_sum([2, 7, 11, 3, 15], 10)
print(result)

