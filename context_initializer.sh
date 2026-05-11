#!/bin/bash

OUTPUT_FILE="project_snapshot.txt"

# 1. Start with the Background
cat << 'EOF' > "$OUTPUT_FILE"
I am going to give you context of the project I need you to help me with.  don't interrupt until I say 'DONE'
###COLLABORATION
I'm in charge.  only generate the code when I ask. when you do give me code, it should be wrapped in a bash script which utilizes a 
'cat until EOF' to genenerate a complete replacement file.  We are using uv.  Any new libraries should be included
in the generated script as a 'uv add' statement.

When we are debugging an issue, I will start by giving you ouput to analyze.  We will discuss the problem and potential 
solutions.  We will decide on the best approach before you start spitting out code.

Never suggest changes within the targets folder.  This is only a work area.  

please reconcile every suggested prompt with this directive:
"We will not give project-specific, library-specific, tech-stack-specific hints or constraints to the ai."

We will not modify snapshot files to get past a node.

one final piece of background info: I am building this for two purposes.. first, I think it is a cool project and want to see it successful. 
second, I want to build skills, create a portfolio piece, and position myself to get a job as a software engineer in the age of ai.  I have a strong software development background but I am trying to shift from being programmer centric to ai centric
### PROJECT TREE
EOF

# 2. Add the Tree
tree -L 3 -I "__pycache__|.git|.venv|workspaces|targets" >> "$OUTPUT_FILE"

# 2.5 Add README
echo -e "\n--- FILE: README.md ---" >> "$OUTPUT_FILE"
cat "README.md" >> "$OUTPUT_FILE"

# 3. Add pyproject.toml
echo -e "\n### ROOT CONFIGURATION (pyproject.toml)" >> "$OUTPUT_FILE"
if [ -f "pyproject.toml" ]; then
    cat "pyproject.toml" >> "$OUTPUT_FILE"
else
    echo "pyproject.toml not found." >> "$OUTPUT_FILE"
fi

# 4. Add all files in the src tree
echo -e "\n### SOURCE CODE" >> "$OUTPUT_FILE"

find src -name "*.py" -not -path "*/__pycache__/*" | while read -r file; do
    echo -e "\n--- FILE: $file ---" >> "$OUTPUT_FILE"
    cat "$file" >> "$OUTPUT_FILE"
done

echo "✅ Context snapshot created: $OUTPUT_FILE"
