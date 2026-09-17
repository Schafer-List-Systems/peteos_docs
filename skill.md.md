# PeteOs SKILL.md

The PeteOS SKILL.md is a markdown file that can be provided to agentic systems like claude code or opencode to give them context about using peteOS correctly. 

## Download
Clone the repository or download `skills/peteos/SKILL.md` directly from [https://github.com/Schafer-List-Systems/peteskill](https://github.com/Schafer-List-Systems/peteskill).

## Installation Steps
1. Find your skills directory: e.g. `myProject/{.claude|.agents|.opencode}/skills`
2. Create a peteos folder in your skills directory
3. Copy the `.md` skill file to your newly created skills/peteos directory
4. Restart your coding assistant

## Verification
Test the skill by prompting your assistant: "How to make a python class intelligent?"
You should be seeing an agent tool call `Load Skill peteos` (or similar, depending on your harness) as part of the reasoning process.
