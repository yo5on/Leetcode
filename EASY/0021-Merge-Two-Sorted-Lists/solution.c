/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     struct ListNode *next;
 * };
 */
struct ListNode* mergeTwoLists(struct ListNode* list1, struct ListNode* list2) {
    // Step 1 -- Check some special situations..
    if (list1 == NULL) 
        return list2;
    else if (list2 == NULL) 
        return list1;
    if (list1 == NULL && list2 == NULL)
        return NULL;

    // Step 2 -- Create Linked List and add first element.
    struct ListNode* root=(struct ListNode*)malloc(sizeof(struct ListNode));
    if(list1->val > list2->val){
        root->val=list2->val;
        list2=list2->next;
    }
    else{
        root->val=list1->val;
        list1=list1->next;
    }
    struct ListNode* iter=root; // I will use iteration to continue on our new list.
   
    // Step 3 -- While both lists are not NULL, do the necessary operations.
    while(list1 != NULL && list2 != NULL){
        iter->next=(struct ListNode*)malloc(sizeof(struct ListNode));
        iter=iter->next;
        if(list1->val >list2->val){
            iter->val=list2->val;
            list2=list2->next;
        }
        else{
            iter->val=list1->val;
            list1=list1->next;
        }

    }

    // Step 4 -- One of them reach NULL, but other list is still NOT NULL. So, continue to add.
    if(list1 == NULL && list2 != NULL){
        while(list2 != NULL){
            iter->next=(struct ListNode*)malloc(sizeof(struct ListNode));
            iter=iter->next;
            iter->val=list2->val;
            list2=list2->next;
        }
    }
    else if(list1 != NULL && list2 == NULL){
        while(list1 != NULL){
            iter->next=(struct ListNode*)malloc(sizeof(struct ListNode));
            iter=iter->next;
            iter->val=list1->val;
            list1=list1->next;
        }
    }

    iter->next=NULL; // Last node's pointer must point somewhere and that is NULL.
    return root; // return our merged list !!
}