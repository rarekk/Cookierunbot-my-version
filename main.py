"""Console-debug entry point that runs the windowless dashboard (``main.pyw``).

``python main.py``  -> launches the dashboard with a console attached (debugging).
``pythonw main.pyw``-> launches completely windowless (production / START_BOT.bat).

All real UI code lives in ``main.pyw``; this file is kept as a compatibility
shim for anyone who still launches via ``main.py``.
"""

import os
import runpy
import sys

_here = os.path.dirname(os.path.abspath(__file__))
sys.argv[0] = os.path.join(_here, "main.pyw")
runpy.run_path(sys.argv[0], run_name="__main__")