#!/bin/bash

# Directory containing the Markdown files
DIRECTORY="_newsletter"

# Create a temporary file to store unique titles
TEMP_FILE=$(mktemp)

# Iterate through all Markdown files
find "$DIRECTORY" -name "*.md" | while read -r FILE; do
  # Extract the title and content_type
  TITLE=$(grep -m 1 '^title:' "$FILE" | sed 's/title: //')
  CONTENT_TYPE=$(grep -m 1 '^content_type:' "$FILE" | sed 's/content_type: //')

  # Check if the title is already seen
  if grep -qF "$TITLE" "$TEMP_FILE"; then
    # If content_type is "analysis", delete the file
    if [ "$CONTENT_TYPE" == "analysis" ]; then
      echo "Deleting $FILE with title $TITLE and content_type $CONTENT_TYPE"
      rm "$FILE"
    fi
  else
    # If title is not seen, add it to the temporary file
    echo "$TITLE" >> "$TEMP_FILE"
  fi
done

# Clean up temporary file
rm "$TEMP_FILE"

echo "Done!"
