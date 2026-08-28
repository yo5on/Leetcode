/**
 * Definition for a binary tree node.
 * public class TreeNode {
 *     int val;
 *     TreeNode left;
## *     TreeNode right;
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
    public List<List<Integer>> pathSum(TreeNode root, int targetSum) {
        final var res = new ArrayList<List<Integer>>();
        dfs(res, new ArrayList<Integer>(), root, targetSum, 0);
        return res;
    }

    public void dfs(final List<List<Integer>> arr, final List<Integer> tempBox, final TreeNode node, final int targetSum, final int currentSum) {
        if (node == null) return;

        tempBox.add(node.val);
        if (node.left != null) {
            dfs(arr, tempBox, node.left, targetSum, currentSum + node.val);
            tempBox.removeLast();
        }
        if (node.right != null) {
            dfs(arr, tempBox, node.right, targetSum, currentSum + node.val);
            tempBox.removeLast();
        }
        if (node.left == null && node.right == null && targetSum == currentSum + node.val) {
            arr.add(new ArrayList<>(tempBox));
            return;
        }
    }
}