class Solution {
    public boolean isPalindrome(int x) {
        if(x<0)
        return false;
        if(x==0)
        return true;
        int n=x;
        String y="";
     while(x>0){
        int l=x%10;
        y=y+l;
        x=x/10;
        }   
        if(y.equals(String.valueOf(n)))
        return true;
        else
        return false;
    }
}