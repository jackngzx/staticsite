from textnode import TextNode, TextType
from blocktype import BlockType
from htmlnode import HTMLNode, LeafNode, ParentNode
import re
import os
import shutil

def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    if text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    if text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    if text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    if text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    if text_node.text_type == TextType.IMAGE:
        return LeafNode(
            "img",
            "",
            {
                "src": text_node.url,
                "alt": text_node.text,
            },
        )
    else:
        raise Exception("No TextNode type matched")


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)

        else:
            # split the text of node with delimiter. result will be a list
            sections = node.text.split(delimiter)
            if len(sections) % 2 == 0:
                raise Exception("Delimiter error, invalid Markdown syntax")
            # assign each of the items in the list into a new node
            for i in range(0, len(sections)):
                if i % 2 == 0:
                    new_node = TextNode(sections[i], TextType.TEXT)
                    new_nodes.append(new_node)
                else:
                    new_node = TextNode(sections[i], text_type)
                    new_nodes.append(new_node)

    return new_nodes


def extract_markdown_images(text):
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches


def extract_markdown_links(text):
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)

        else:
            image_tuples = extract_markdown_images(node.text)
            if image_tuples == []:
                new_nodes.append(node)
            else:
                current_text = node.text
                for image in image_tuples:
                    image_alt = image[0]
                    image_url = image[1]
                    sections = current_text.split(f"![{image_alt}]({image_url})" , 1)
                    if sections[0] != "":
                        new_nodes.append(TextNode(f"{sections[0]}", TextType.TEXT))
                    new_nodes.append(TextNode(f"{image_alt}", TextType.IMAGE, f"{image_url}"))
                    current_text = sections[1]
                if current_text != "":
                    new_nodes.append(TextNode(f"{current_text}", TextType.TEXT))
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)

        else:
            link_tuples = extract_markdown_links(node.text)
            if link_tuples == []:
                new_nodes.append(node)
            else:
                current_text = node.text
                for link in link_tuples:
                    link_alt = link[0]
                    link_url = link[1]
                    sections = current_text.split(f"[{link_alt}]({link_url})" , 1)
                    if sections[0] != "":
                        new_nodes.append(TextNode(f"{sections[0]}", TextType.TEXT))
                    new_nodes.append(TextNode(f"{link_alt}", TextType.LINK, f"{link_url}"))
                    current_text = sections[1]
                if current_text != "":
                    new_nodes.append(TextNode(f"{current_text}", TextType.TEXT))
    return new_nodes

def text_to_textnodes(text):
    result = []
    old_node = TextNode(text, TextType.TEXT)
    new_nodes = split_nodes_delimiter([old_node], "**", TextType.BOLD)
    new_nodes = split_nodes_delimiter(new_nodes, "_", TextType.ITALIC)
    new_nodes = split_nodes_delimiter(new_nodes, "`", TextType.CODE)
    new_nodes = split_nodes_image(new_nodes)
    new_nodes = split_nodes_link(new_nodes)
    result.extend(new_nodes)

    return result

def markdown_to_blocks(markdown):
    result = []
    blocks = markdown.split('\n\n')
    for block in blocks:
        block = block.strip()
        if block != "":
            result.append(block)

    return result

def block_to_block_type(block):
    lines = block.split("\n")
    if re.match(r'#{1,6}\s', block):
        return BlockType.HEADING
    if re.match(r'>\s', block):
        return BlockType.QUOTE
    if block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE
    if block.startswith("- "):
        for line in lines:
            if not line.startswith("- "):
                return BlockType.PARAGRAPH
        return BlockType.UNORDERED_LIST
    if block.startswith("1. "):
        i = 1
        for line in lines:
            if not line.startswith(f"{i}. "):
                return BlockType.PARAGRAPH
            i += 1
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    child_nodes = []
    for node in text_nodes:
        child_nodes.append(text_node_to_html_node(node))
    return child_nodes

def paragraph_to_html_node(block):
    lines = block.split("\n")
    stripped = [line.strip() for line in lines]
    string = " ".join(stripped)
    child_nodes = text_to_children(string)
    return ParentNode("p", child_nodes, None)
    
def heading_to_html_node(block):
    level = 0
    for char in block:
        if char == "#" and level < 6:
            level += 1
        else:
            break
    text = block[level + 1:]
    children = text_to_children(text)
    return ParentNode(f"h{level}", children, None)

def quote_to_html_node(block):
    lines = block.split("\n")
    child_nodes = []
    for line in lines:
       cleaned_line = line.lstrip(">")
       child_nodes.append(cleaned_line.strip())
    text = " ".join(child_nodes)
    children = text_to_children(text)
    return ParentNode("blockquote", children, None)

def ul_to_html_node(block):
    lines = block.split("\n")
    child_nodes = []
    for line in lines:
        text = line[2:].strip()
        children = text_to_children(text)
        child_node = ParentNode("li", children)
        child_nodes.append(child_node)
    return ParentNode("ul", child_nodes, None)

def ol_to_html_node(block):
    lines = block.split("\n")
    child_nodes = []
    for line in lines:
        parts = line.split(". ", 1)
        text = parts[1].strip()
        children = text_to_children(text)
        child_node = ParentNode("li", children)
        child_nodes.append(child_node)
    return ParentNode("ol", child_nodes, None)

def code_to_html_node(block):
    lines = block.split("\n")
    stripped = [line.strip() for line in lines]
    inner_lines = stripped[1:-1]
    text = "\n".join(inner_lines) + "\n"
    text_node = TextNode(text, TextType.TEXT)
    html_node = text_node_to_html_node(text_node)
    child_node = ParentNode("code", [html_node])
    return ParentNode("pre", [child_node])

def block_to_html_node(block):
    blocktype = block_to_block_type(block)
    if blocktype == BlockType.HEADING:
        return heading_to_html_node(block)
    elif blocktype == BlockType.CODE:
        return code_to_html_node(block)
    elif blocktype == BlockType.ORDERED_LIST:
        return ol_to_html_node(block)
    elif blocktype == BlockType.UNORDERED_LIST:
        return ul_to_html_node(block)
    elif blocktype == BlockType.QUOTE:
        return quote_to_html_node(block)
    elif blocktype == BlockType.PARAGRAPH:
        return paragraph_to_html_node(block)
    else:
        raise ValueError("Invalid BlockType")

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        html_node = block_to_html_node(block)
        children.append(html_node)
    return ParentNode("div", children, None)

def extract_title(markdown):
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        lines = block.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("# "):
                return stripped[2:]
    raise Exception("No title found")

def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    # file at from path
    with open(from_path, "r") as from_file:
        from_file_md = from_file.read()
        from_file_html_string = markdown_to_html_node(from_file_md).to_html()
        page_title = extract_title(from_file_md)
    with open(template_path, "r") as template_file:
        template_data = template_file.read()
        full_page = template_data
        full_page = full_page.replace("{{ Title }}", page_title)
        full_page = full_page.replace("{{ Content }}", from_file_html_string)
        full_page = full_page.replace('href="/', f'href="{basepath}')
        full_page = full_page.replace('src="/', f'src="{basepath}')
        
        dest_dir = os.path.dirname(dest_path)
        if dest_dir != "":
            os.makedirs(dest_dir, exist_ok=True)
        with open(dest_path, "w") as file:
            file.write(full_page)
            
def copy_content(source_dir, destination_dir):
    if not os.path.exists(destination_dir):
        os.mkdir(destination_dir)
    if os.path.exists(source_dir):
        items = os.listdir(source_dir)
        for item in items:
            path_to_item = os.path.join(source_dir, item)
            if os.path.isfile(path_to_item):
                shutil.copy(path_to_item, destination_dir)
            if os.path.isdir(path_to_item):
                path_to_directory = os.path.join(destination_dir, item)
                if not os.path.exists(path_to_directory):
                    os.mkdir(path_to_directory)
                copy_content(path_to_item, path_to_directory)
    else:
        raise Exception("Source directory does not exist")

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    # find content directory
    content_dir = os.listdir(dir_path_content)
    # check each item in content directory
    for item in content_dir:
        path_to_item = os.path.join(dir_path_content, item)
        if os.path.isfile(path_to_item):
            root, ext = os.path.splitext(item)
            destination_file = root + ".html"
            path_to_dest = os.path.join(dest_dir_path, destination_file)
            generate_page(path_to_item, template_path, path_to_dest, basepath)
        if os.path.isdir(path_to_item):
            path_to_dest = os.path.join(dest_dir_path, item)
            generate_pages_recursive(path_to_item, template_path, path_to_dest, basepath)

