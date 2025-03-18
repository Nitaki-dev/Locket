
create env:
`python -m venv password_managercd `

open env:
`cd env\password_manager\Scripts\`
`activate.bat`

compile:
`pyinstaller --onefile --noconsole --collect-data sv_ttk main.py`

when it finished compiling, the exe is located under `\env\dist`

todo: 
- fix the EDIT function actually edit the service name