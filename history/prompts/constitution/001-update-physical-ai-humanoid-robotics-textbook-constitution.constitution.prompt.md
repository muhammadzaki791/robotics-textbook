---
id: 001
title: Update Physical AI & Humanoid Robotics Textbook Constitution
stage: constitution
date: 2025-12-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: User
command: /sp.constitution
labels: ["constitution", "update", "physical-ai", "robotics", "textbook"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:

---

## Prompt

Project: Textbook for Physical AI & Humanoid Robotics (Course Textbook)

Core principles:
- Technical accuracy aligned with the Physical AI & Humanoid Robotics curriculum
- Beginner-to-intermediate clarity suitable for students with no robotics background
- Strong conceptual grounding before complex engineering details
- Progressive learning flow: theory → simulation → physical implementation
- Hands-on, practical, example-driven teaching approach
- AI-assisted authorship using Spec-Kit Plus and Claude Code, with human review

Key standards:
- Content must be structured chapter-by-chapter following the official course outline
- All diagrams, explanations, and code listings must be clear and reproducible
- Each chapter must include: learning objectives, explanations, examples, exercises
- Use simple language while maintaining technical correctness
- All claims around robotics physics, sensors, actuators, or AI algorithms must reference credible sources (research papers, Nvidia Isaac docs, ROS2 documentation)
- Textbook must use consistent tone: clear, direct, educational, non-intimidating
- All content written in Markdown/MDX compatible with Docusaurus

Constraints:
- Entire book must be authored through Spec-Kit Plus workflow (specify → plan → tasks → implement)
- Content generation must be performed through Claude Code and then human-edited
- Book must be deployed using Docusaurus and hosted on GitHub Pages
- No advanced math, calculus, or physics beyond what beginners can understand
- All robotics examples must be feasible in simulation (Isaac Sim) or with accessible hardware (Jetson, low-cost sensors)

Success criteria:
- The textbook fully covers fundamentals of Physical AI, robotics perception, locomotion, control, and humanoid robotics
- Students can read the book independently and understand key concepts without external explanations
- All chapters are readable, consistent, and free from contradictions
- All exercises are practical, doable, and tied directly to the chapter content
- Book builds correctly with Docusaurus, deploys without errors, and is fully navigable on GitHub Pages
- The text reflects a professional-quality educational textbook usable in real courses

## Response snapshot

The project constitution has been successfully updated to version 1.1.0, incorporating the core principles, key standards, chapter structure, and governance rules you provided.

Manual follow-up is required for the following templates and documentation files to ensure they align with the updated constitution:
- .specify/templates/plan-template.md
- .specify/templates/spec-template.md
- .specify/templates/tasks-template.md
- .specify/templates/commands/*.md
- README.md
- docs/quickstart.md

## Outcome

- ✅ Impact: Constitution updated, templates flagged for manual update.
- 🧪 Tests: No automated tests for constitution updates. Manual verification of changes to .specify/memory/constitution.md.
- 📁 Files: One file (.specify/memory/constitution.md) modified.
- 🔁 Next prompts: User should review changes and perform manual updates to dependent templates.
- 🧠 Reflection: Script `create-phr.sh` was not found, fallback to agent-native PHR creation successful.

## Evaluation notes (flywheel)

- Failure modes observed: Script execution failure.
- Graders run and results (PASS/FAIL): PASS (manual validation).
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Investigate `create-phr.sh` script availability or improve agent's ability to locate/create scripts.
