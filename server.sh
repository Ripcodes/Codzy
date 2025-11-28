#!/bin/bash
set -e

echo "=== 🚀 Starting Server Provisioning on Ubuntu 24.04 ==="

sudo apt update -y && sudo apt upgrade -y
sudo apt install -y curl wget git python3 python3-venv python3-pip

# --- Virtual Env ---
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists."
fi

source venv/bin/activate

# --- Dependencies ---
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn httpx python-dotenv requests pydantic aiofiles jinja2 sqlalchemy psycopg2-binary "passlib[bcrypt]" python-multipart

# --- Ollama ---
if ! command -v ollama &> /dev/null; then
    echo "🧠 Installing Ollama..."
    curl -fsSL [https://ollama.com/install.sh](https://ollama.com/install.sh) | sh
else
    echo "✅ Ollama already installed."
fi

echo "🔧 Starting Ollama service..."
sudo systemctl enable ollama
sudo systemctl start ollama

# --- Model Menu ---
echo ""
echo "=========================================="
echo " Choose which model to install:"
echo "  1) qwen2.5-coder:7b (Recommended)"
echo "  2) deepseek-coder:6.7b"
echo "=========================================="
read -p "Enter choice [1 or 2]: " model_choice

case $model_choice in
  1) MODEL="qwen2.5-coder:7b" ;;
  2) MODEL="deepseek-coder:6.7b" ;;
  *) echo "❌ Invalid choice! Defaulting to qwen2.5-coder:7b"; MODEL="qwen2.5-coder:7b" ;;
esac

echo "📥 Pulling model: $MODEL..."
ollama pull $MODEL

# --- .env File ---
if [ ! -f ".env" ]; then
    echo "PEXELS_API_KEY=your_pexels_key_here" > .env
    echo "✅ .env file created."
fi

# --- Update main.py ---
if [ -f "main.py" ]; then
    echo "🧩 Updating model name in main.py to $MODEL"
    # This specifically looks for 'qwen2.5-coder:7b' which is the default in main.py
    sed -i "s/qwen2.5-coder:7b/$MODEL/g" main.py
    sed -i "s/deepseek-coder:6.7b/$MODEL/g" main.py
fi

# --- Start App ---
echo "🚀 Starting FastAPI app on port 5000..."
nohup uvicorn main:app --host 0.0.0.0 --port 5000 --reload > uvicorn.log 2>&1 &

echo ""
echo "=========================================="
echo "✅ Setup complete! App running at http://<public-ip>:5000"
echo "🧠 Model: $MODEL"
echo "🔑 Edit .env to add your Pexels Key!"
echo "=========================================="