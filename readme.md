
open env:
`python -m venv myEnv`


compile:
`pyinstaller --onefile --collect-data sv_ttkd main.py`

when it finished compiling, the exe is located under `\app\dist`

todo: 
- fix theme crashing app
- save the password files to an actual location
- fix the EDIT function actually edit the service name