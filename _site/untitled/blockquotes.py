import os
import re

# Define the directory where the .md files are located
directory = '/Users/frankemanuele/Documents/GitHub/blog/untitled'

# Define the regular expression pattern to match the figure element
pattern = r'<figure.*?>\s*<span>(.*?)</span>\s*</figure>'

# Compile the regular expression pattern
regex = re.compile(pattern, re.DOTALL)

# Loop through each file in the directory
for filename in os.listdir(directory):
    if filename.endswith('.md'):
        # Read the contents of the file
        with open(os.path.join(directory, filename), 'r') as file:
            contents = file.read()
        
        # Extract the text string using regex
        match = regex.search(contents)
        if match:
            text_string = match.group(1)
            
            # Remove any remaining HTML tags from the text string
            text_string = re.sub(r'<.*?>', '', text_string)
            
            # Write the updated contents back to the file
            with open(os.path.join(directory, filename), 'w') as file:
                file.write(text_string)
