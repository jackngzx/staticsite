import os
import shutil
from functions import copy_content, generate_pages_recursive

def main():
    source = "content"
    destination = "public"

    if os.path.exists(destination):
        shutil.rmtree(destination)
    copy_content("static", "public")
    generate_pages_recursive(source, "template.html", destination)
    
main()