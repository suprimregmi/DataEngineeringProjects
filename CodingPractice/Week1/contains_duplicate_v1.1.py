class Solution:
    def contains_duplicate(self, nums: list[int]) -> bool:
        seen = set()
        for val in nums:
            if val in seen:
                return True
            seen.add(val)
        return False


print(Solution().contains_duplicate([1,2,3,1]))   # True
print(Solution().contains_duplicate([1,2,3,4]))   # False
print(Solution().contains_duplicate([1,1,1,3,3,4,3,2,4,2]))  # True
print(Solution().contains_duplicate([]))          # False
print(Solution().contains_duplicate([7]))         # False