"""Given a non-empty array of integers nums, every element appears twice except for one. Find that single one.
#136 Single Number` — Dict / XOR — Easy
You must implement a solution with a linear runtime complexity and use only constant extra space.*/"""


def single_num(nums):
    result =0
    for n in num:
        result ^=n
    return result