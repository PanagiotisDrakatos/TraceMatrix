
# 🔍 OSINT Stack (100% Open-Source) — Dockerized

Ένα πλήρως **ανοιχτού κώδικα** OSINT (Open Source Intelligence) stack που συνδυάζει σύγχρονες τεχνολογίες αναζήτησης, scraping, και ανάλυσης δεδομένων.

## 📦 Τι Περιλαμβάνει

### Core Services

- **🎯 Orchestrator (FastAPI)** — Κεντρικό API με πολλαπλά connectors:
  - Google Custom Search Engine (CSE)
  - SearXNG integration (metasearch engine)
  - Reacher (email verification)
  - Social-Analyzer (username OSINT)
  - Trafilatura (intelligent web scraping)
  - Sentence-Transformers (semantic embeddings)
  
- **🔎 OpenSearch** — Full-text search με:
  - BM25 ranking algorithm
  - k-NN vector search
  - Hybrid Search με RRF (Reciprocal Rank Fusion)

- **📊 OpenSearch Dashboards** — Web UI για visualization και exploration
- **🌐 SearXNG** — Privacy-respecting metasearch engine
- **✉️ Reacher** — Email verification service
- **🔗 Social-Analyzer** — Username enumeration σε 1000+ platforms
- **⚡ Redis** — Caching layer για performance

### Key Features

✅ Web scraping με semantic analysis  
✅ Hybrid search (BM25 + vector embeddings)  
✅ Email verification  
✅ Social media username enumeration  
✅ CSV export για Maltego CE integration  
✅ 100% open-source stack  

---

## 🚀 Τρέξιμο

### Προαπαιτούμενα

- Docker & Docker Compose εγκατεστημένα
- (Προαιρετικά) Google Programmable Search API credentials

### Βήματα Εγκατάστασης

**1. Clone το repository:**
```bash
git clone <repo-url>
cd Osint
```

**2. Ρύθμιση Environment Variables:**

Αντίγραψε το `.env.example` σε `.env` και συμπλήρωσε τα δικά σου credentials:

```bash
# Linux/Mac
cp .env.example .env

# Windows
copy .env.example .env
```

Άνοιξε το `.env` και άλλαξε τις τιμές:

```env
# Google Custom Search Engine (προαιρετικό)
GOOGLE_CSE_API_KEY=your_google_cse_api_key_here
GOOGLE_CSE_CX=your_google_cse_cx_here

# SearXNG Secret (άλλαξε σε τυχαίο string)
SEARXNG_SECRET_KEY=change_this_to_a_random_string

# OpenSearch Password (άλλαξε σε ισχυρό password)
OPENSEARCH_INITIAL_ADMIN_PASSWORD=change_this_to_a_strong_password

# Τα υπόλοιπα μπορούν να μείνουν ως έχουν
```

> ⚠️ **ΣΗΜΑΝΤΙΚΟ:** Μην κάνεις commit το `.env` file! Είναι ήδη στο `.gitignore` για την ασφάλειά σου.

> 💡 Αν δεν ορίσεις τα Google CSE credentials, το `/search` endpoint θα λειτουργεί με περιορισμένες δυνατότητες (μόνο SearXNG).

**3. Εκκίνηση του stack:**
```bash
docker compose up --build
```

Περίμενε μέχρι να σηκωθούν όλα τα services (~2-3 λεπτά για πρώτη φορά).

---

## 🌐 Διαθέσιμα Services

| Service | URL | Περιγραφή |
|---------|-----|-----------|
| **Orchestrator API** | http://localhost:8000/docs | FastAPI Swagger UI (interactive docs) |
| **SearXNG** | http://localhost:8081 | Metasearch engine interface |
| **OpenSearch** | http://localhost:9200 | Search engine API |
| **OpenSearch Dashboards** | http://localhost:5601 | Data visualization & exploration |
| **Reacher** | http://localhost:8082 | Email verification service |
| **Social-Analyzer** | http://localhost:9000 | Username enumeration tool |

---

## 📡 API Endpoints

### Διαθέσιμα Endpoints

| Endpoint | Method | Περιγραφή |
|----------|--------|-----------|
| `/search` | POST | Βασική αναζήτηση με Google CSE / SearXNG + profession filtering |
| `/verify_email` | POST | Email verification μέσω Reacher |
| `/ingest_urls` | POST | Scraping, embedding generation & OpenSearch indexing |
| `/search_hybrid` | POST | Hybrid search (BM25 + k-NN + RRF fusion) |
| `/social_lookup` | POST | Username enumeration σε 1000+ social platforms |
| `/export_csv` | GET | Export δεδομένων σε CSV format για Maltego |

Για **πλήρη τεκμηρίωση** και **interactive testing**, άνοιξε το Swagger UI: http://localhost:8000/docs

---

## 💡 Παραδείγματα Χρήσης

### 🔎 Web Search με Profession Filtering

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Γιώργος Παπαδόπουλος",
    "keywords": ["αρχιτέκτονας"],
    "limit": 5
  }'
```

### 🔗 Social Media Username Lookup

```bash
curl -X POST "http://localhost:8000/social_lookup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "giorgospapadopoulos"
  }'
```

### 📥 Ingest & Index URLs

```bash
curl -X POST "http://localhost:8000/ingest_urls" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://example.com/portfolio"],
    "source": "web"
  }'
```

### 🎯 Hybrid Search (BM25 + Vector)

```bash
curl -X POST "http://localhost:8000/search_hybrid" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Giorgos Papadopoulos architect Athens",
    "k": 10
  }'
```

### ✉️ Email Verification

```bash
curl -X POST "http://localhost:8000/verify_email" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "example@domain.com"
  }'
```

### 📊 Export για Maltego CE

```bash
curl "http://localhost:8000/export_csv"
```

Το αρχείο δημιουργείται στο: `orchestrator/exports/entities.csv`

**Import στο Maltego CE:**
1. Άνοιξε το Maltego CE
2. Πήγαινε στο **Import** → **CSV**
3. Διάλεξε το `entities.csv` αρχείο
4. Map τα πεδία σύμφωνα με τις οδηγίες

---

## 🎯 Workflows & Σενάρια Χρήσης

### Πότε να χρησιμοποιήσεις ποιο endpoint;

#### 1️⃣ Θέλω απλώς να δω αν "υπάρχει" κάποιος + ρόλος/επάγγελμα

**Βήματα:**
```bash
# 1. Βασική αναζήτηση με name + keywords
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Γιώργος Παπαδόπουλος",
    "keywords": ["αρχιτέκτονας"],
    "limit": 10
  }'

# 2. (Προαιρετικά) Verify email αν βρεθεί
curl -X POST "http://localhost:8000/verify_email" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "giorgos.papadopoulos@example.com"
  }'

# 3. (Προαιρετικά) Social lookup για footprints
curl -X POST "http://localhost:8000/social_lookup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "giorgospapadopoulos"
  }'
```

**Γιατί αυτό;**
- ✅ Ελάχιστη τριβή, γρήγορο αποτέλεσμα
- ✅ Μικρό κόστος (Google CSE quota)
- ✅ Ideal για quick checks

---

#### 2️⃣ Θέλω usernames/προφίλ από πολλές πλατφόρμες

**Βήματα:**
```bash
# Πήγαινε κατευθείαν σε Social-Analyzer
curl -X POST "http://localhost:8000/social_lookup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "giorgospapadopoulos"
  }'
```

**Γιατί αυτό;**
- ✅ Στοχευμένο για social media
- ✅ Χωρίς Google quota
- ✅ Συχνά πιο "καθαρά" hits για handles
- ✅ 1000+ platforms σε ένα call

---

#### 3️⃣ Θέλω υψηλή ακρίβεια και fast follow-up queries χωρίς ξανά πληρωμές

**Βήματα:**
```bash
# 1. Μάζεψε τις καλύτερες σελίδες (URLs)
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Γιώργος Παπαδόπουλος",
    "keywords": ["αρχιτέκτονας", "Athens"],
    "limit": 20
  }'

# 2. Ingest τα URLs (batch processing)
curl -X POST "http://localhost:8000/ingest_urls" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://example.com/profile1",
      "https://example.com/profile2",
      "https://linkedin.com/in/...",
      "... (20-200 URLs)"
    ],
    "source": "web_search"
  }'

# 3. Τρέξε πολλαπλές αναζητήσεις με hybrid search (γρήγορα & δωρεάν)
curl -X POST "http://localhost:8000/search_hybrid" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Giorgos Papadopoulos architect Athens portfolio",
    "k": 10
  }'

curl -X POST "http://localhost:8000/search_hybrid" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "architectural projects Greece 2024",
    "k": 10
  }'
```

**Γιατί αυτό;**
- ✅ Μετά το πρώτο ingest, οι αναζητήσεις είναι πολύ γρήγορες
- ✅ Δεν "καίνε" Google quota για follow-up queries
- ✅ Το ranking βελτιώνεται (BM25 + k-NN + RRF)
- ✅ Ιδανικό για deep research

---

#### 4️⃣ Θέλω γραφάκι/αναφορά

**Βήματα:**
```bash
# Όταν καταλήξεις στα entities, export σε CSV
curl "http://localhost:8000/export_csv" -o entities.csv

# Άνοιξε στο Maltego CE:
# 1. Maltego CE → Import → CSV
# 2. Διάλεξε το entities.csv
# 3. Map τα πεδία (name, url, source, κτλ.)
# 4. Visualize το graph
```

**Γιατί αυτό;**
- ✅ Δεν χρειάζεται σε κάθε run
- ✅ Μόνο για export/οπτικοποίηση
- ✅ Ideal για παρουσιάσεις/reports

---

## 📋 2 Προτεινόμενες "Συνταγές"

### Συνταγή A: Quick Lookup (3 κλήσεις max)

**Use case:** Γρήγορη επαλήθευση ύπαρξης ατόμου

```bash
# Step 1: Web search
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"name":"Γιώργος Παπαδόπουλος","keywords":["αρχιτέκτονας"],"limit":15}'

# Step 2: Social lookup
curl -X POST "http://localhost:8000/social_lookup" \
  -H "Content-Type: application/json" \
  -d '{"username":"giorgospapadopoulos"}'

# Step 3: Email verification (μόνο για υποψήφια emails)
curl -X POST "http://localhost:8000/verify_email" \
  -H "Content-Type: application/json" \
  -d '{"email":"giorgos.p@example.com"}'
```

**⏱️ Χρόνος:** 30-60 δευτερόλεπτα  
**💰 Κόστος:** Χαμηλό (χρησιμοποιεί Google μόνο 1 φορά)  
**🎯 Ideal για:** Initial reconnaissance, quick checks

---

### Συνταγή B: Deep Research + Γρήγορα Επόμενα Runs (Index-First)

**Use case:** Βαθιά έρευνα με πολλαπλά queries

```bash
# Step 1: Αρχική αναζήτηση για URLs
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"name":"Γιώργος Παπαδόπουλος","keywords":["αρχιτέκτονας"],"limit":50}'

# Step 2: Batch ingest (20-200 URLs)
curl -X POST "http://localhost:8000/ingest_urls" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://site1.com/profile",
      "https://site2.com/portfolio",
      "... (50-200 URLs)"
    ],
    "source": "batch_research"
  }'

# Step 3: Πολλαπλές hybrid searches (γρήγορα, χωρίς επιπλέον κόστος)
curl -X POST "http://localhost:8000/search_hybrid" \
  -H "Content-Type: application/json" \
  -d '{"query":"architectural projects Athens 2024","k":10}'

curl -X POST "http://localhost:8000/search_hybrid" \
  -H "Content-Type: application/json" \
  -d '{"query":"sustainable building design Greece","k":10}'

curl -X POST "http://localhost:8000/search_hybrid" \
  -H "Content-Type: application/json" \
  -d '{"query":"Giorgos Papadopoulos awards publications","k":10}'

# Step 4: Export για αναφορά (αν χρειάζεται)
curl "http://localhost:8000/export_csv" -o final_report.csv
```

**⏱️ Χρόνος:** 5-15 λεπτά για setup, μετά <1 δευτερόλεπτο/query  
**💰 Κόστος:** Κυρίως στο πρώτο step, μετά σχεδόν μηδενικό  
**🎯 Ideal για:** Deep investigations, research projects, multiple angles

---

## ⚡ Απόδοση & Tips

### Γενικές Οδηγίες

- **Δεν χρειάζονται όλα κάθε φορά** — Συνδύασε `/search` + `/social_lookup` για τα περισσότερα cases
- **Social lookup δεν "καίει" quotas** — Αλλά τρέχει πολλούς ελέγχους, οπότε χρησιμοποίησε timeouts αν το αυτοματοποιήσεις
- **Email precision** — Πάντα πέρασε υποψήφια emails από `/verify_email` πριν τα θεωρήσεις valid

### Για Κλιμάκωση/Ταχύτητα

Αν θες να επενδύσεις στο `/ingest_urls` + `/search_hybrid`:

**1. Batch Size Optimization:**
```bash
# Optimal: 50-200 URLs ανά batch
curl -X POST "http://localhost:8000/ingest_urls" \
  -H "Content-Type: application/json" \
  -d '{"urls":[/* 50-200 URLs */],"source":"batch"}'
```

**2. Embedding Configuration:**
```bash
# Στο orchestrator/.env ή environment:
EMBED_DIM=384  # Για balance μεταξύ ταχύτητας/ποιότητας
# EMBED_DIM=768  # Αν έχεις RAM και θέλεις καλύτερη ακρίβεια
```

**3. Docker Resources:**
```yaml
# Στο docker-compose.yml:
services:
  orchestrator:
    deploy:
      resources:
        limits:
          memory: 4G  # Minimum για embeddings
  opensearch:
    deploy:
      resources:
        limits:
          memory: 2G  # Για k-NN vectors
```

**Συνολικό recommended RAM:** 4-6GB για όλο το stack

### Quota Control

**Caching για Google CSE** (μείωση API calls):
```bash
# Το Redis είναι ήδη στο stack - enable caching:
# Στο orchestrator/main.py, πρόσθεσε TTL 7-30 ημέρες για search results
```

**Πλεονεκτήματα:**
- ✅ Ίδιο query → instant response από cache
- ✅ Μείωση Google CSE quota usage κατά ~60-80%
- ✅ Faster response times

---

## 🛠️ Επεκτάσεις & Customization

Αυτό το stack είναι ένα **starter template**. Μπορείς να το επεκτείνεις με:

### Προτεινόμενα Additional Tools

- **[Sherlock](https://github.com/sherlock-project/sherlock)** — Username search across 400+ social networks
- **[Maigret](https://github.com/soxoj/maigret)** — Collect info about person by username
- **[theHarvester](https://github.com/laramies/theHarvester)** — Email, subdomain & people intelligence
- **[PhoneInfoga](https://github.com/sundowndev/phoneinfoga)** — Phone number OSINT
- **[SpiderFoot](https://github.com/smicallef/spiderfoot)** — Automated OSINT reconnaissance
- **[Holehe](https://github.com/megadose/holehe)** — Check if email is used on different sites

### Customization Tips

- Πρόσθεσε δικούς σου connectors στο `orchestrator/` directory
- Τροποποίησε τα profession filters στο `profession_filter.py`
- Customize τα embedding models στο `scrape_embed.py`
- Ρύθμισε το OpenSearch schema για τις ανάγκες σου

---

## 📝 License

Open-source project. Χρησιμοποίησε υπεύθυνα και σύμφωνα με τους νόμους της χώρας σου.

## ⚠️ Disclaimer

Αυτό το εργαλείο είναι για **νόμιμη OSINT έρευνα** και **εκπαιδευτικούς σκοπούς**. Ο χρήστης είναι υπεύθυνος για τη νόμιμη χρήση του λογισμικού.
