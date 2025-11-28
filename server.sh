#!/bin/bash
set -e

echo "=== 🚀 Starting Server Provisioning on Ubuntu 24.04 ==="

# --- Update and Upgrade Packages ---
sudo apt update -y && sudo apt upgrade -y

# --- Install System Dependencies ---
sudo apt install -y curl wget git python3 python3-venv python3-pip

# --- Virtual Environment Setup ---
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists."
fi

# Activate venv to install packages
source venv/bin/activate

# --- Upgrade pip and Install Python Dependencies ---
echo "📚 Installing required Python packages..."
pip install --upgrade pip
# Added python-dotenv for Pexels API key management
pip install fastapi uvicorn httpx python-dotenv requests pydantic aiofiles jinja2 sqlalchemy psycopg2-binary "passlib[bcrypt]" python-multipart

# --- Install Ollama (FIXED) ---
if ! command -v ollama &> /dev/null; then
    echo "🧠 Installing Ollama..."
    # FIXED: Removed markdown syntax [url](url) -> plain url
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "✅ Ollama already installed."
fi

# --- Start and Enable Ollama Service ---
echo "🔧 Starting Ollama service..."
sudo systemctl enable ollama
sudo systemctl start ollama

# --- Model Selection ---
echo ""
echo "=========================================="
echo " Choose which model to install:"
echo "  1) qwen2.5-coder:7b (Recommended - Fast & Smart)"
echo "  2) deepseek-coder:6.7b (Good alternative)"
echo "=========================================="
read -p "Enter choice [1 or 2]: " model_choice

case $model_choice in
  1) MODEL="qwen2.5-coder:7b" ;;
  2) MODEL="deepseek-coder:6.7b" ;;
  *) echo "❌ Invalid choice! Defaulting to qwen2.5-coder:7b"; MODEL="qwen2.5-coder:7b" ;;
esac

# --- Pull Selected Model ---
echo "📥 Pulling model: $MODEL (this may take a while)..."
ollama pull $MODEL

# --- Create .env file ---
if [ ! -f ".env" ]; then
    echo "🔑 Creating .env file..."
    echo "PEXELS_API_KEY=your_pexels_key_here" > .env
    echo "✅ .env file created."
else
    echo "✅ .env file already exists."
fi

# --- Update main.py Model Reference ---
if [ -f "main.py" ]; then
    echo "🧩 Updating model name in main.py to $MODEL"
    # Replaces default or previously set model names with the selected one
    sed -i "s/qwen2.5-coder:7b/$MODEL/g" main.py
    sed -i "s/deepseek-coder:6.7b/$MODEL/g" main.py
fi

# --- Start FastAPI App ---
echo "🚀 Starting FastAPI app on port 5000..."

# Notes:
# 1. Uses ./venv/bin/uvicorn to ensure we use the venv python.
# 2. Adds --timeout-keep-alive 600 to fix frontend timeouts (10 minutes).
nohup ./venv/bin/uvicorn main:app --host 0.0.0.0 --port 5000 --timeout-keep-alive 600 --reload > uvicorn.log 2>&1 &

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "🌐 Your app is running at: http://<your-public-ip>:5000"
echo "🧠 Model used: $MODEL"
echo "⏳ Timeout set to: 600 seconds (10 mins)"
echo "🔑 ACTION REQUIRED: Run 'nano .env' and paste your Pexels API key!"
echo "📄 Logs: tail -f uvicorn.log"
echo "=========================================="