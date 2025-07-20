#!/usr/bin/env python3
"""
Fix emoji characters in custom_mcp_llm_iteration.py that are causing syntax errors
"""

import re

def remove_emojis_from_file(file_path):
    """Remove emoji characters from logger statements"""
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define emoji patterns commonly used in logger statements
    emoji_replacements = {
        '🎯': '',
        '🚀': '',
        '⚡': '',
        '🔧': '',
        '📊': '',
        '🤖': '',
        '💡': '',
        '✅': '',
        '❌': '',
        '⏱️': '',
        '🧪': '',
        '🔍': '',
        '📋': '',
        '📈': '',
        '🎉': '',
        '🔄': '',
        '🌐': '',
        '💬': '',
        '📁': '',
        '🛠️': '',
        '⚙️': '',
        '🎲': '',
        '🎪': '',
        '🎨': '',
        '🎭': '',
        '🎬': '',
        '🎮': '',
        '🎯': '',
        '🌟': '',
        '⭐': '',
        '🔥': '',
        '💥': '',
        '💯': '',
        '🚨': '',
        '⚠️': '',
        '🔔': '',
        '📣': '',
        '📢': '',
        '📡': '',
        '🔗': '',
        '🧠': '',
        '💻': '',
        '📱': '',
        '🖥️': '',
        '⌨️': '',
        '🖱️': '',
        '🖨️': '',
        '📀': '',
        '💾': '',
        '💿': '',
        '📱': '',
        '📞': '',
        '☎️': '',
        '📧': '',
        '📨': '',
        '📩': '',
        '📪': '',
        '📫': '',
        '📬': '',
        '📭': '',
        '📮': '',
        '🗂️': '',
        '📂': '',
        '📃': '',
        '📄': '',
        '📑': '',
        '📊': '',
        '📈': '',
        '📉': '',
        '📋': '',
        '📌': '',
        '📍': '',
        '📎': '',
        '📏': '',
        '📐': '',
        '✂️': '',
        '🔒': '',
        '🔓': '',
        '🔐': '',
        '🔑': '',
        '🗝️': '',
        '🔨': '',
        '⛏️': '',
        '🔧': '',
        '🔩': '',
        '⚙️': '',
        '🛠️': '',
        '⚖️': '',
        '🔗': '',
        '⛓️': '',
        '🧰': '',
        '🧲': '',
    }
    
    # Apply replacements
    for emoji, replacement in emoji_replacements.items():
        content = content.replace(emoji, replacement)
    
    # Clean up extra spaces that might result from emoji removal
    content = re.sub(r'logger\.(info|error|warning|debug)\(f?"([^"]*?)  +([^"]*?)"\)', r'logger.\1(f"\2 \3")', content)
    content = re.sub(r'logger\.(info|error|warning|debug)\(f?" +([^"]*?)"\)', r'logger.\1(f"\2")', content)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Removed emojis from {file_path}")

if __name__ == "__main__":
    file_path = "mcp/custom_mcp_llm_iteration.py"
    remove_emojis_from_file(file_path)
    print("✅ Emoji cleanup complete!")
