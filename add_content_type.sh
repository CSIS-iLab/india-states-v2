#!/bin/bash

# Directory containing the Markdown files
DIRECTORY="_newsletter/"

# Iterate through all Markdown files
find "$DIRECTORY" -name "*.md" | while read -r FILE; do
  # Check if the file is missing the content_type field
  if ! grep -q '^content_type:' "$FILE"; then
    echo "Adding content_type: newsletter to $FILE"
    
    # Insert 'content_type: newsletter' after the first '---'
    awk 'NR==1{print; print "content_type: newsletter"; next}1' "$FILE" > temp && mv temp "$FILE"
  fi
done

echo "Done!"
