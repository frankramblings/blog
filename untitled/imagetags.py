import os
import re

# Define the directory where the .md files are located
directory = '/Users/frankemanuele/Documents/GitHub/blog/untitled'

# Define the regular expression pattern to match the div element
pattern = r'<div class="\s*image-block-outer-wrapper\s*layout-caption-below\s*design-layout-inline\s*"\s*data-test="image-block-inline-outer-wrapper"><figure class="\s*sqs-block-image-figure\s*intrinsic\s*"\s*style="max-width:\d+px;"><div class="\s*image-block-wrapper\s*"[^>]*><div class="\s*sqs-image-shape-container-element\s*has-aspect-ratio\s*"[^>]*>.*?</div></div></figure></div>'

# Compile the regular expression pattern
regex = re.compile(pattern)

# Loop through each file in the directory
for filename in os.listdir(directory):
    if filename.endswith('.md'):
        # Read the contents of the file
        with open(os.path.join(directory, filename), 'r') as file:
            contents = file.read()
        
        # Remove the specified div element using regex
        new_contents = regex.sub('', contents)
        
        # Write the updated contents back to the file
        with open(os.path.join(directory, filename), 'w') as file:
            file.write(new_contents)
