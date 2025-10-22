# 🔒 Security Notice

## ⚠️ ΠΡΟΣΟΧΗ: API Keys έχουν εκτεθεί

Το repository αυτό περιέχει **hardcoded API keys** σε προηγούμενα commits που πρέπει να θεωρηθούν **εκτεθειμένα**:

- Google CSE API Key: `AIzaSyAHccfDlj4_wb5-XnfviNrianyNkLaV1xI`
- Google CSE CX: `f4e6d444f64204539`

### 🛠️ Άμεσες Ενέργειες που Πρέπει να Κάνεις:

1. **Ακύρωση Google API Key:**
   - Πήγαινε στο [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Βρες το API key και κάνε "Delete" ή "Restrict"
   - Δημιούργησε νέο API key

2. **Δημιουργία νέων credentials:**
   - Άνοιξε το `.env` file
   - Βάλε τα νέα credentials εκεί
   - ΜΗΝ κάνεις commit το `.env` file

3. **Καθαρισμός Git History (Προαιρετικό αλλά Συνιστάται):**
   
   Αν θέλεις να αφαιρέσεις τα credentials από όλο το Git history:
   
   ```bash
   # Χρησιμοποίησε το BFG Repo-Cleaner
   # https://rtyley.github.io/bfg-repo-cleaner/
   
   # Ή χρησιμοποίησε git-filter-repo
   git filter-repo --invert-paths --path docker-compose.yml
   ```
   
   > ⚠️ Αυτό θα ξαναγράψει το history και θα χρειαστεί force push!

### 📝 Από εδώ και πέρα:

Το repository είναι τώρα ρυθμισμένο σωστά:
- ✅ Το `.env` file είναι στο `.gitignore`
- ✅ Το `docker-compose.yml` χρησιμοποιεί μεταβλητές περιβάλλοντος
- ✅ Το `.env.example` παρέχει template για νέους χρήστες

**Πάντα ελέγχεις πριν κάνεις commit:**
```bash
git status
git diff
```

Αν δεις οποιοδήποτε API key ή password, ΜΗΝ το κάνεις commit!

