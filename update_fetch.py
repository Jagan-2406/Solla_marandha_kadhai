import os, glob

# Process HTML files
html_files = glob.glob('frontend/*.html')
for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Insert config.js before main.js or other scripts
    if '<script src="/static/js/config.js"></script>' not in content:
        if '<script src="/static/js/main.js">' in content:
            content = content.replace('<script src="/static/js/main.js">', '<script src="/static/js/config.js"></script>\n  <script src="/static/js/main.js">')
        elif '</head>' in content:
            content = content.replace('</head>', '  <script src="/static/js/config.js"></script>\n</head>')
    
    # Replace fetch calls
    content = content.replace('fetch("/', 'fetch(API_BASE_URL + "/')
    content = content.replace("fetch('/", "fetch(API_BASE_URL + '/")
    content = content.replace('fetch(`/api', 'fetch(API_BASE_URL + `/api')
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

# Process main.js
main_js = 'frontend/static/js/main.js'
with open(main_js, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace fetch calls
content = content.replace('fetch("/', 'fetch(API_BASE_URL + "/')
content = content.replace("fetch('/", "fetch(API_BASE_URL + '/")
content = content.replace('fetch(`/api', 'fetch(API_BASE_URL + `/api')

with open(main_js, 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated fetch calls in frontend.')
