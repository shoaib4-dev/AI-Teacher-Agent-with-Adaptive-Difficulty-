# Gemini API Key Setup Guide

## Quick Setup

1. **Open the `.env` file** in the project root (same folder as `requirements.txt`)

2. **Replace the placeholder with your actual Gemini API key:**
   ```
   GEMINI_API_KEY=your-actual-gemini-api-key-here
   ```

3. **Save the file**

4. **Install the Gemini package:**
   ```powershell
   pip install langchain-google-genai
   ```

5. **Restart the backend** - The API key will be loaded automatically

## Example

Your `.env` file should look like this:
```
GEMINI_API_KEY=AIzaSyC-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Get Your API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and paste it in `.env` file

## Verify It's Working

When you start the backend, if the API key is loaded correctly, you won't see any error messages. The agent will use Gemini for AI features.

## Important Notes

- The `.env` file is in the project root (where `requirements.txt` is)
- Don't share your `.env` file or commit it to Git
- The app works without API key (uses fallback methods)
- Restart the backend after changing the API key

