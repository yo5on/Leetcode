class Solution {
    public int[] twoSum(int[] nums, int target) {
        int a[] = new int[2],i;
        for(i=0;i<nums.length;i++){
            for(int j=i+1;j<nums.length;j++){
                if(nums[i]+nums[j]==target){
                    a[0] = i;
                    a[1] = j;
                    break;
                }
            }
        }
        if(i==nums.length)
        return a;
        else 
        return a;
    }
}