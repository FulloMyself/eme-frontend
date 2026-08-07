@"
import sys
import os

# Add your application directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app import app as application
"@ | Out-File -FilePath passenger_wsgi.py -Encoding UTF8