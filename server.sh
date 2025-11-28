#!/bin/bash
set -e

echo "=== 🚀 Starting Server Provisioning on Ubuntu 24.04 ==="

# --- Update and Upgrade Packages ---
sudo apt update -y && sudo apt upgrade -y

# --- Install System Dependencies ---
sudo apt install -y curl wget git python3 python3-venv python3-pip

# --- Verify pip Installation ---
if ! command -v pip &> /dev/null; then
    echo "pip not found, installing manually..."
    curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3
else
    echo "✅ pip already installed."
fi

# --- Create and Activate Python Virtual Environment ---
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists."
fi

source venv/bin/activate

# --- Upgrade pip and Install Dependencies ---
echo "📚 Installing required Python packages..."
pip install --upgrade pip
pip install fastapi uvicorn httpx python-dotenv requests pydantic aiofiles jinja2 sqlalchemy psycopg2-binary "passlib[bcrypt]" python-multipart

# --- Install Ollama ---
if ! command -v ollama &> /dev/null; then
    echo "🧠 Installing Ollama..."
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
echo " Choose which GPT-OSS model to install:"
echo "  1) gpt-oss:20b"
echo "  2) gpt-oss:120b"
echo "=========================================="
read -p "Enter choice [1 or 2]: " model_choice

case $model_choice in
  1)
    MODEL="gpt-oss:20b"
    ;;
  2)
    MODEL="gpt-oss:120b"
    ;;
  *)
    echo "❌ Invalid choice! Defaulting to gpt-oss:20b"
    MODEL="gpt-oss:20b"
    ;;
esac

# --- Pull Selected Model ---
echo "📥 Pulling model: $MODEL (this may take a while)..."
ollama pull $MODEL

# --- Update main.py Model Reference (both places) ---
if [ -f "main.py" ]; then
    echo "🧩 Updating model name in main.py to $MODEL"
    sed -i "s/gpt-oss:120b/$MODEL/g" main.py
    sed -i "s/gpt-oss:20b/$MODEL/g" main.py
else
    echo "⚠️ main.py not found in current directory!"
    echo "Please add your project files before running the app."
    exit 1
fi

# --- Start FastAPI App ---
echo "🚀 Starting FastAPI app on port 5000..."
nohup uvicorn main:app --host 0.0.0.0 --port 5000 --reload > uvicorn.log 2>&1 &

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "🌐 Your app is running at: http://<your-ec2-public-ip>:5000"
echo "🧠 Model used: $MODEL"
echo "📄 Logs: ./uvicorn.log"
echo ""
echo "To view logs: tail -f uvicorn.log"
echo "To stop app: pkill -f 'uvicorn main:app'"
echo "=========================================="