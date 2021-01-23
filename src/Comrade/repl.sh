# Run this on repl.it as your main.sh
while :
do
rm -rf Comrade
git clone --branch master https://github.com/itchono/Comrade
cp -a Comrade/src/Comrade/. .
pip install -r requirements.txt
python main.py
done