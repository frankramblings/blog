import re
import os

# Define the regular expression pattern
pattern = re.compile(r'/blog/(\d{4})/(\d{2})/(\d{2})/\d{4}-\d{1,2}-\d{1,2}-')

# Define the directory where the text files are located
directory = '/Users/frankemanuele/Documents/GitHub/blog/untitled'

# Loop through each file in the directory
for filename in os.listdir(directory):
    if filename.endswith('.md'):
        # Read the contents of the file
        with open(os.path.join(directory, filename), 'r') as file:
            contents = file.read()
        
        # Apply the regular expression to replace the text string
        new_contents = re.sub(pattern, r'/\1/\2/\3/', contents)
        
        # Write the updated contents back to the file
        with open(os.path.join(directory, filename), 'w') as file:
            file.write(new_contents)