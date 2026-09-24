class Solution {
    public boolean searchMatrix(int[][] matrix, int target) {

        int m = matrix.length;
        int n = matrix[0].length;

        int left = 0;
        int right = m*n-1;

        while(left<=right){
            int position = (right+left)/2;

            int row = position/n;
            int col = position%n;

            if(matrix[row][col]== target){
                return true;
            }

            if(matrix[row][col] > target){
                right = position-1;
            }else{
                left = position +1;
            }
            


        } 


        return false;
        
    }
}