import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(HERE)
# Simplemente arranca app.py (que ya tiene el auto-instalador dentro)
exec(open(os.path.join(HERE, "app.py")).read())
