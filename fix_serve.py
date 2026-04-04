with open('api_server.py', 'r') as f:
    content = f.read()

# Fix the function to serve login.html
content = content.replace(
    "web_file = os.path.join(os.path.dirname(__file__), 'web_interface.html')",
    "web_file = os.path.join(os.path.dirname(__file__), 'login.html')"
)

with open('api_server.py', 'w') as f:
    f.write(content)

print("✅ Fixed: Now serving login.html")
