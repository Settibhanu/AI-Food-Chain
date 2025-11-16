# AI4Bharat Indic-TTS Setup Instructions for Kannada

## Step 1: Clone the Repository

Open your terminal in the project directory and run:

```bash
cd "E:\WITFluence_AI-entire food chain\AI-Food-Chain"
git clone https://github.com/AI4Bharat/Indic-TTS.git
```

## Step 2: Install System Dependencies (Windows)

For Windows, you'll need:
- **FFmpeg**: Download from https://ffmpeg.org/download.html and add to PATH
- **libsndfile**: Usually comes with Python packages, but you may need to install via conda or pip

Or use conda to install:
```bash
conda install -c conda-forge libsndfile ffmpeg
```

## Step 3: Install Python Dependencies

Navigate to the Indic-TTS directory and install requirements:

```bash
cd Indic-TTS
pip install -r requirements.txt
```

**Note**: Indic-TTS requires Python 3.9-3.11. If you're using Python 3.13, you may need to:
- Use a virtual environment with Python 3.11, OR
- Install dependencies manually and handle compatibility issues

## Step 4: Download Kannada Models

Download the pre-trained Kannada models from AI4Bharat:

1. Visit: https://github.com/AI4Bharat/Indic-TTS (check the README for model download links)
2. Download the Kannada model files
3. Extract and place them in the following structure:

```
Indic-TTS/
  Kannada/
    fastpitch/
      best_model.pth
    config.json
    hifigan/
      best_model.pth
      config.json
```

**Alternative**: Check the repository for direct download links or use their model download script if available.

## Step 5: Test the Setup

Test if Indic-TTS works:

```bash
cd Indic-TTS
python -m TTS.bin.synthesize --text "ನಮಸ್ಕಾರ" \
    --model_path Kannada/fastpitch/best_model.pth \
    --config_path Kannada/config.json \
    --vocoder_path Kannada/hifigan/best_model.pth \
    --vocoder_config_path Kannada/hifigan/config.json \
    --out_path test_output.wav
```

## Step 6: Restart Flask Server

Once setup is complete, restart your Flask server. The code will automatically detect and use Indic-TTS for Kannada.

## Troubleshooting

1. **Python Version Issues**: If you have Python 3.13, consider using a virtual environment with Python 3.11
2. **Import Errors**: Make sure all dependencies are installed and Indic-TTS is in the correct location
3. **Model Not Found**: Verify the model files are in the correct directory structure
4. **CUDA Issues**: If you have GPU, ensure PyTorch with CUDA is installed

## Current Status

- ✅ Browser TTS for English (works immediately)
- ✅ Browser TTS for Hindi (works immediately)  
- ⚠️ AI4Bharat Indic-TTS for Kannada (requires setup above)

