
# How to compile:
`python -m venv locket`
`pip3 install -r req.txt`

put main.py and req.txt inside the `locket` folder

`cd locket\Scripts\`
`activate.bat`
`cd ..`
`pip install -r req.txt`

`pyinstaller --onefile --collect-data sv_ttk main.py`
(You can add `--noconsole`, but this triggers a false positive for my antivirus)


open env if you need to recompile:
`cd env\locket\Scripts\`
`activate.bat`

compile:
`pyinstaller --onefile --collect-data sv_ttk main.py`

when it finished compiling, the exe is located under `\env\dist`
