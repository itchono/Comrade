ARR=($(find ../../src -type f | while read in ; do if file -i "${in}" | grep -q x-python ; then echo "${in}" ; fi ; done))

for fp in "${ARR[@]}"
do
        python3 -m yapf --in-place "$fp"
done
