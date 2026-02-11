# 🚀 Quick Start Checklist

## ✅ Installation Complete!

All dependencies are installed. Follow this checklist to get your backend running:

---

## 📋 Pre-Flight Checklist

### Step 1: Verify Installation ✅
```bash
cd C:\Users\HP\Documents\Week2Bootcamp\backend
python -c "import fastapi, pandas, torch, transformers, faiss; print('✅ Ready!')"
```
**Status:** ✅ DONE

---

### Step 2: Copy Your Dataset ⚠️ REQUIRED
**File needed:** `historical_events_cleaned_full.csv`

**Copy to:**
```
C:\Users\HP\Documents\Week2Bootcamp\backend\app\data\documents\historical_events_cleaned_full.csv
```

**Quick method:**
```bash
cd C:\Users\HP\Documents\Week2Bootcamp\backend
setup_dataset.bat
```

**Status:** ⏳ DO THIS NOW

---

### Step 3: Review Configuration (Optional)
Edit `.env` file if needed:
```bash
# Already configured with defaults
# You can optionally add:
# EXTERNAL_LLM_API_URL=https://api.openai.com/v1/chat/completions
# EXTERNAL_LLM_API_KEY=your-key
```

**Status:** ✅ Already configured (can skip)

---

### Step 4: Start the Server
```bash
cd C:\Users\HP\Documents\Week2Bootcamp\backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
🏛️  HISTORICAL RAG SYSTEM STARTUP
Loading Historical BERT...
✅ Historical BERT loaded
Initializing RAG System...
Loading dataset from app/data/documents/historical_events_cleaned_full.csv
Creating document chunks...
Generating embeddings...
✅ RAG System initialized
✅ SYSTEM READY
🌐 Server running at http://0.0.0.0:8000
```

**First run:** 5-15 minutes (downloads models, processes data)  
**Subsequent runs:** 30 seconds (uses cache)

**Status:** ⏳ AFTER YOU COPY DATASET

---

### Step 5: Test the API
**Open in browser:**
```
http://localhost:8000/docs
```

**Or test with curl:**
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models_loaded": {
    "historical_bert": true,
    "rag_system": true,
    "llm_service": true
  },
  "documents_indexed": 1534,
  "device": "cpu"
}
```

**Status:** ⏳ AFTER SERVER STARTS

---

### Step 6: Connect Frontend
Update your frontend `.env`:
```env
VITE_API_URL=http://localhost:8000
```

Or update `ChatInterface.tsx`:
```typescript
const CHAT_URL = 'http://localhost:8000/api/chat';
```

**Status:** ⏳ AFTER BACKEND WORKS

---

## 🎯 Success Criteria

You'll know everything is working when:

✅ Server starts without errors  
✅ Health check returns "healthy"  
✅ `/docs` page loads  
✅ Frontend can connect and chat  
✅ Characters respond in their unique voices  

---

## 🐛 Troubleshooting

### "Dataset not found"
→ Copy CSV to `backend/app/data/documents/historical_events_cleaned_full.csv`

### "Cannot import name..."
→ Run: `pip install -r requirements.txt --force-reinstall`

### Server won't start
→ Check Python version: `python --version` (need 3.9+)

### Port 8000 in use
→ Change port: `python -m uvicorn app.main:app --port 8001`

### First run is slow
→ Normal! Downloading models (~2GB). Be patient.

---

## 📞 Quick Help

**View logs:**
Server shows detailed logs in console - watch for errors

**Restart server:**
Press `Ctrl+C` then run uvicorn command again

**Clear cache:**
Delete `backend/app/data/faiss_index/` folder to rebuild from scratch

---

## ✅ Current Status

- [x] Dependencies installed
- [ ] Dataset copied → **DO THIS NEXT!**
- [ ] Server started
- [ ] API tested
- [ ] Frontend connected

---

**You're 1 step away from a working backend!**

Just copy your dataset CSV and run the server! 🚀

---

*Need detailed help? See SETUP.md or COMPLETE.md*

