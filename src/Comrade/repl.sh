rm -rf Comrade
git clone --branch v5-rewrite https://github.com/itchono/Comrade
cp -a Comrade/src/Comrade/. .
pip install -r requirements.txt
python main.py