import pkg_resources
import sys

required_packages = {
    'flask',
    'openai',
    'replicate',
    'python-dotenv',
    'requests'
}

installed_packages = {pkg.key for pkg in pkg_resources.working_set}
missing_packages = required_packages - installed_packages

print("Python version:", sys.version)
print("\nChecking required packages...")
print("Installed packages:", installed_packages)
print("Missing packages:", missing_packages)

if missing_packages:
    print("\nPlease install missing packages using:")
    print(f"pip install {' '.join(missing_packages)}")
else:
    print("\nAll required packages are installed!") 