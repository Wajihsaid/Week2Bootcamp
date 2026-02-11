# Installation Guide for Future Reference

## Quick Install (All at Once)

```bash
cd backend

# Method 1: Install PyTorch from official repo, then rest
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# Method 2: Install everything step by step (more reliable on Windows)
pip install fastapi uvicorn[standard] python-multipart pydantic pydantic-settings python-jose
pip install numpy pandas
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install transformers sentence-transformers
pip install faiss-cpu edge-tts SpeechRecognition pydub aiofiles loguru
```

## Troubleshooting

### If pandas fails to install:
```bash
# Pandas sometimes needs to build from source on Windows
# Solution: Let pip find the right pre-built wheel
pip install numpy pandas
```

### If PyTorch fails:
```bash
# Use official PyTorch CPU-only wheels
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### If FAISS fails:
```bash
# Use CPU version (no compilation needed)
pip install faiss-cpu
```

## Verification

Test that everything works:
```bash
python -c "import fastapi; import pandas; import torch; import transformers; import sentence_transformers; import faiss; import edge_tts; print('✅ All good!')"
```

## Notes

- Python 3.9+ required
- Windows users: No Visual Studio build tools needed with this approach
- All packages use pre-built wheels (no compilation)
- Total download size: ~3GB
- Installation time: 5-10 minutes

---

**Installation tested and working on:**
- Windows 11
- Python 3.14
- Date: February 11, 2026

