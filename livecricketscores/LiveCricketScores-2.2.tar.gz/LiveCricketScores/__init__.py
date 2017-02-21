import os

if os.system('python -c "import requests"') != 0:
	os.system('pip install requests"')

if os.system('python -c "from bs4 import BeautifulSoup"') != 0:
	os.system('pip install bs4"')