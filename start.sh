echo "Starting Engine..."

# 1. Check if the bot files are already here (to avoid overwriting your manual changes)
if [ -f "main.py" ]; then
    echo "Files found locally. Skipping Clone..."
else
    # 2. If files are missing, Clone YOUR Repository (LastPerson07), not the original one
    echo "Files not found. Cloning Repo...."
    
    if [ -z "$BRANCH" ]; then
        echo "Cloning main branch...."
        # UPDATED REPO URL to yours
        git clone https://github.com/LastPerson07/Ultra-Forward-Bot Ultra-Forward-Bot
    else
        echo "Cloning $BRANCH branch...."
        git clone https://github.com/LastPerson07/Ultra-Forward-Bot -b $BRANCH Ultra-Forward-Bot
    fi
    
    # Enter the directory
    cd Ultra-Forward-Bot || exit
fi

# 3. Install Dependencies
echo "Installing Requirements..."
pip3 install -U -r requirements.txt

# 4. Start the 10x Speed Bot
echo "Starting Ultra-Forward-Bot..."
python3 main.py

