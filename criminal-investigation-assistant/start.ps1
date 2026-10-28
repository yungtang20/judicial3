$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
py -3 -X utf8 -m app.server
