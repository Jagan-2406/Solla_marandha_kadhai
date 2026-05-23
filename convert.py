import zipfile
import xml.etree.ElementTree as ET
import os

def docx_to_txt(docx_path, txt_path):
    try:
        if not os.path.exists(docx_path):
            print(f"File not found: {docx_path}")
            return
        with zipfile.ZipFile(docx_path) as z:
            xml_content = z.read('word/document.xml')
            root = ET.fromstring(xml_content)
            
            # Namespaces for Word XML parsing
            namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            paragraphs = []
            # Find all paragraph elements
            for p in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                texts = []
                # Find all text elements within the paragraph
                for r in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                    if r.text:
                        texts.append(r.text)
                paragraphs.append("".join(texts))
            
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(paragraphs))
            print(f"Successfully converted {docx_path} to {txt_path}")
    except Exception as e:
        print(f"Error converting {docx_path}: {e}")

# Convert both documents
docx_to_txt("Tamil_NLP_Complete_Project_Guide_complete roadmap.docx", "roadmap.txt")
docx_to_txt("Tamil_NLP_Setup_Guide.docx", "setup_guide.txt")
