import os

# Define the directory where the .md files are located
directory = '/Users/frankemanuele/Documents/GitHub/blog/untitled'

# Loop through each file in the directory
for filename in os.listdir(directory):
    if filename.endswith('.md'):
        # Read the contents of the file
        with open(os.path.join(directory, filename), 'r') as file:
            contents = file.read()
        
        # Remove the specified string
        new_contents = contents.replace('</div></div></figure></div>')
        
        # Write the updated contents back to the file
        with open(os.path.join(directory, filename), 'w') as file:
            file.write(new_contents)
