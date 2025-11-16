# Quick Setup Guide - Kannada TTS with AI4Bharat Indic-TTS

## Current Status ✅
- ✅ Indic-TTS repository cloned
- ✅ Kannada models present in `Indic-TTS/Kannada/`
- ✅ Code updated to use correct API
- ⚠️ TTS library needs to be installed

## Step-by-Step Instructions

### Step 1: Activate Your Python 3.9 Environment

Open your terminal (Command Prompt or PowerShell) and run:

```bash
conda activate witfluence-chatbot-39
```

Verify Python version:
```bash
python --version
```
Should show: `Python 3.9.x`

### Step 2: Install TTS Library

**Option A: Using Conda (Recommended - No compilation needed)**
```bash
conda install -c conda-forge coqui-tts -y
```

**Option B: If Option A doesn't work, install dependencies via conda first:**
```bash
conda install -c conda-forge spacy librosa -y
pip install TTS
```

**Option C: If both fail, install Visual C++ Build Tools:**
1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install "Desktop development with C++" workload
3. Restart terminal
4. Then: `pip install TTS`

### Step 3: Install Other Indic-TTS Dependencies

```bash
cd "E:\WITFluence_AI-entire food chain\AI-Food-Chain\Indic-TTS"
pip install -r requirements.txt
```

(Note: TTS is commented out in requirements.txt, so it won't try to install it again)

### Step 4: Test TTS Installation

```bash
python -c "from TTS.utils.synthesizer import Synthesizer; print('TTS imported successfully!')"
```

If this works, you're good to go!

### Step 5: Restart Your Flask Server

```bash
cd "E:\WITFluence_AI-entire food chain\AI-Food-Chain"
python app.py
```

### Step 6: Test Kannada TTS

1. Open your browser and go to the chatbot
2. Select Kannada language
3. Ask a question in Kannada (or use voice input)
4. The response should be spoken in Kannada using AI4Bharat Indic-TTS

## Troubleshooting

**If TTS import fails:**
- Make sure you're in Python 3.9 environment
- Try: `pip install --upgrade TTS`
- Check: `python -c "import TTS; print(TTS.__version__)"`

**If models not found:**
- Verify: `Indic-TTS/Kannada/fastptich/best_model.pth` exists
- Check the path in app.py matches your directory structure

**If audio doesn't play:**
- Check browser console for errors
- Verify Flask server logs show "AI4Bharat Indic-TTS for Kannada loaded successfully!"

## What's Working Now

- ✅ **English**: Browser TTS (works immediately)
- ✅ **Hindi**: Browser TTS (works immediately)
- ⚠️ **Kannada**: AI4Bharat Indic-TTS (needs TTS library installed - Step 2)

## Next Steps After Setup

Once TTS is installed and Flask server is running:
1. Test English/Hindi first (should work immediately)
2. Test Kannada (will use AI4Bharat Indic-TTS)
3. Check server logs for any errors

Good luck! 🚀

