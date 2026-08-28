class Solution {
    public ListNode removeNthFromEnd(ListNode head, int n) {

        int length = 0;
        ListNode temp = head;

        while (temp != null) {
            length++;
            temp = temp.next;
        }

        // Remove first node
        if (length == n)
            return head.next;

        int steps = length - n - 1;

        ListNode prev = head;

        while (steps > 0) {
            prev = prev.next;
            steps--;
        }

        prev.next = prev.next.next;

        return head;
    }
}