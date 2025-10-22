# 🔒 Security Notice

## ⚠️ WARNING: API Keys Have Been Exposed

This repository contains **hardcoded API keys** in previous commits that should be considered **exposed**:

- Google CSE API Key: `AIzaSyAHccfDlj4_wb5-XnfviNrianyNkLaV1xI`
- Google CSE CX: `f4e6d444f64204539`

### 🛠️ Immediate Actions You Must Take:

1. **Revoke Google API Key:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Find the API key and click "Delete" or "Restrict"
   - Create a new API key

2. **Create New Credentials:**
   - Open the `.env` file
   - Add the new credentials there
   - DO NOT commit the `.env` file

3. **Clean Git History (Optional but Recommended):**
   
   If you want to remove credentials from the entire Git history:
   
   ```bash
   # Use BFG Repo-Cleaner
   # https://rtyley.github.io/bfg-repo-cleaner/
   
   # Or use git-filter-repo
   git filter-repo --invert-paths --path docker-compose.yml
   ```
   
   > ⚠️ This will rewrite history and require a force push!

### 📝 From Now On:

The repository is now properly configured:
- ✅ The `.env` file is in `.gitignore`
- ✅ `docker-compose.yml` uses environment variables
- ✅ `.env.example` provides a template for new users

**Always check before committing:**
```bash
git status
git diff
```

If you see any API key or password, DO NOT commit it!

