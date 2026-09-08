cd C:\JavaScript\petrie
taskkill /f /im python.exe /im py.exe /im PetrieQuote.exe
rmdir /s /q build dist

py -m PyInstaller --noconfirm --onedir --windowed --name "PetrieQuote" --add-data "index.html;." SERVER.PY

:: Copy assets folder and individual files into dist\PetrieQuote
xcopy /e /i /y assets dist\PetrieQuote\assets
copy /y logo.png dist\PetrieQuote\
copy /y clients.json dist\PetrieQuote\
copy /y presets.json dist\PetrieQuote\
copy /y terms.json dist\PetrieQuote\
copy /y images.json dist\PetrieQuote\

:: Deploy full dist folder to C:\PetrieQuotes
xcopy /e /i /y dist\PetrieQuote C:\PetrieQuotes




PAUSE 0 