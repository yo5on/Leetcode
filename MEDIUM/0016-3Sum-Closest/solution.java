class Solution {
    public int threeSumClosest(int[] nums, int target) {

        Arrays.sort(nums);
        int n = nums.length;
        int diff = Integer.MAX_VALUE;
        int result = 0;

        for (int i = 0; i < n - 2; i++) {
            int left = i + 1;
            int right = n - 1;

            while (left < right){

                int sum = nums[i] + nums[left] + nums[right];
                int d = Math.abs(target - sum);

                if(diff > d){
                    diff = d;
                    result = sum;
                }
                if(sum == target){
                    return result;
                }
                if(sum < target){
                    left++;
                }else{
                    right--;
                }
            }
        }
        return result;
    }
}