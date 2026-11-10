import re

with open('Frontend/Feature/Step_Definition/test_login.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Add import os if missing
if 'import os' not in code:
    code = code.replace('import time', 'import os\nimport time')

# Update fixture
pattern = r'(@pytest\.fixture\(autouse=True\)\s+def anti_race_condition_deliberation_pause\(self\):[\s\S]*?time\.sleep\(5\.0\))'
replacement = '''@pytest.fixture(autouse=True)
    def anti_race_condition_deliberation_pause(self):
        """
        Fixture jeda deliberasi setelah setiap test case selesai
        untuk mencegah race condition pada pengujian mobile automation.
        """
        yield
        delay = 0.05 if os.getenv('HEADLESS_FAST', '0') == '1' else 5.0
        time.sleep(delay)'''

code = re.sub(pattern, replacement, code)

with open('Frontend/Feature/Step_Definition/test_login.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("test_login.py patched successfully.")

