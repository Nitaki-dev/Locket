
create env:
`python -m venv myEnv`

open env:
`cd app\myEnv\Scripts\`
`activate.bat`

compile:
`pyinstaller --onefile --noconsole --collect-data sv_ttkd main.py`

when it finished compiling, the exe is located under `\app\dist`

todo: 
- fix theme crashing app
- save the password files to an actual location
- fix the EDIT function actually edit the service name