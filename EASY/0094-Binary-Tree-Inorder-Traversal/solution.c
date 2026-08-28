/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     struct TreeNode *left;
 *     struct TreeNode *right;
 * };
 */
/**
 * Note: The returned array must be malloced, assume caller calls free().
 */

int root_len(struct TreeNode* root)
{
    if (!root)
        return (0);
    return (1 + root_len(root->right) + root_len(root->left));
}

int*    adding_values(struct TreeNode* root, int* total, int *i)
{
    if (!root)
        return (NULL);
    adding_values(root->left, total, i);
    total[(*i)++] = root->val;
    adding_values(root->right, total, i);
    return (total);
}

int*    inorderTraversal(struct TreeNode* root, int* returnSize)
{
    int *total;
    int i;

    i = 0;
    *returnSize = root_len(root);
    total = malloc(*returnSize * sizeof(int));
    if (!total)
        return (NULL);
    return (adding_values(root, total, &i));
}