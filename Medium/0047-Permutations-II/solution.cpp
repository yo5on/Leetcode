class Solution {
public:
    vector<vector<int>> ans;
    vector<int> curr;
    vector<bool> visited;

    void backtrack(vector<int>& nums) {
        if (curr.size() == nums.size()) {
            ans.push_back(curr);
            return;
        }

        for (int i = 0; i < nums.size(); i++) {
            if (visited[i]) continue;

            if (i > 0 && nums[i] == nums[i - 1] && !visited[i - 1])
                continue;

            visited[i] = true;
            curr.push_back(nums[i]);

            backtrack(nums);

            curr.pop_back();
            visited[i] = false;
        }
    }

    vector<vector<int>> permuteUnique(vector<int>& nums) {
        sort(nums.begin(), nums.end());
        visited.assign(nums.size(), false);

        backtrack(nums);

        return ans;
    }
};