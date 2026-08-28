/**
 * Definition for a binary tree node.
 * public class TreeNode {
 *     int val;
 *     TreeNode left;
 *     TreeNode right;
 *     TreeNode() {}
 *     TreeNode(int val) { this.val = val; }
 *     TreeNode(int val, TreeNode left, TreeNode right) {
 *         this.val = val;
 *         this.left = left;
 *         this.right = right;
 *     }
 * }
 */
class Solution {
    public static int heightTree(TreeNode node){
        if(node == null){
            return 0;
        }
        int leftheight = heightTree(node.left);
        int rightheight = heightTree(node.right);
        if(leftheight == -1){
            return -1;
        }
        if(rightheight == -1){
            return -1;
        }
        
        if(Math.abs(leftheight - rightheight) > 1){
            return -1;
        }

        return 1 + Math.max(leftheight,rightheight);

    }
    public boolean isBalanced(TreeNode root) {
        
        return heightTree(root) != -1;
        
    }
}