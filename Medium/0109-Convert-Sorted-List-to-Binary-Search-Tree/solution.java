class Solution {
    public TreeNode sortedListToBST(ListNode head) {
        if(head == null) return null;
        List<Integer> l = new ArrayList<>();
        while(head != null) {
            l.add(head.val);
            head = head.next;
        }
        return sortedArrayToBST(l);
    }

    private TreeNode sortedArrayToBST(List<Integer> nums) {
        return helper(nums, 0, nums.size() - 1);
    }

    private TreeNode helper(List<Integer> nums, int low, int high) {
        if(low <= high){
            int mid = (low + high) / 2;
            TreeNode root = new TreeNode(nums.get(mid));
            root.left = helper(nums, low, mid - 1);
            root.right = helper(nums, mid + 1, high);

            return root;
        }
        return null;
    }

}