from textnode import TextNode, TextType

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