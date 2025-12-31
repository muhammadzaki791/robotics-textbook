# Chapter Template and Style Guide for Physical AI & Humanoid Robotics Textbook

## Chapter Template

```markdown
---
title: [Chapter Title]
sidebar_position: [Chapter Number]
description: [Brief description of chapter content]
---

# [Chapter Title]

## Learning Objectives

By the end of this chapter, you will be able to:
- [Objective 1]
- [Objective 2]
- [Objective 3]

## Introduction

[Opening paragraph that introduces the topic and connects to previous chapters if applicable]

## [Main Section 1 Name]

[Content for the first main section]

### [Subsection if needed]

[Content for subsection]

## [Main Section 2 Name]

[Content for the second main section]

### [Code Example or Diagram]

```[language]
[Code example in Python, ROS2, or pseudocode]
```

**Explanation:** [Brief explanation of the code example]

### [Diagram Placeholder]

```
[ASCII diagram or description of visual content needed]
```

**Figure [X]:** [Description of what the figure illustrates]

## Summary

[Key takeaways from the chapter, summarizing main concepts]

## Exercises

1. [Exercise question 1]
2. [Exercise question 2]
3. [Mini-project or hands-on activity]

## References and Further Reading

- [Source 1]
- [Source 2]
- [Relevant papers, websites, or textbooks]
```

## Style Guide

### General Writing Principles

1. **Audience**: Write for undergraduate or advanced high-school students with basic programming/math knowledge but no prior robotics experience.

2. **Tone**: Maintain a clear, helpful, encouraging, and suitable tone for students. Avoid unnecessary complexity.

3. **Clarity**: Use precise robotics terminology only when needed and explain it clearly. Break down complex physics and robotics concepts into simple logical steps.

### Formatting Standards

1. **Headings**: Use proper heading hierarchy (H1 for chapter title, H2 for main sections, H3 for subsections)

2. **Lists**: Use bullet points for items without sequence and numbered lists for sequential steps

3. **Emphasis**: Use bold for key terms when first introduced, italics for emphasis

4. **Code Blocks**:
   - Use fenced code blocks with language specification
   - Include comments in code examples
   - Provide brief explanations after code blocks when needed

5. **Diagrams**:
   - Use ASCII diagrams for simple concepts
   - Provide detailed descriptions for complex diagrams that will be created later
   - Always include figure captions

### Technical Standards

1. **Terminology Consistency**: Use consistent terminology throughout the textbook
   - Use "robot" not "Robot" unless at the beginning of a sentence
   - Use "humanoid robot" not "Humanoid Robot"
   - Define acronyms when first used (e.g., "Proportional-Integral-Derivative (PID) controller")

2. **Mathematical Notation**:
   - Use standard mathematical notation
   - Explain mathematical concepts in plain language
   - Use inline math for simple expressions: `$x = y + z$`
   - Use display math for complex equations:
   ```
   $$F = ma$$
   ```

3. **Code Standards**:
   - Use Python conventions for Python code
   - Include comments explaining non-obvious code
   - Use descriptive variable names
   - Include error handling where appropriate

### Content Structure

1. **Learning Objectives**:
   - Limit to 3-5 specific, measurable objectives
   - Use action verbs (identify, explain, implement, analyze)

2. **Sections**:
   - Each section should focus on one main concept
   - Provide examples after introducing new concepts
   - Include at least one exercise per major section

3. **Exercises**:
   - Include a mix of conceptual questions and practical applications
   - Provide difficulty levels if needed (beginner, intermediate)
   - Include mini-projects that connect to real robotics applications

### Quality Standards

1. **Accuracy**: Ensure all technical explanations are correct. When citing external facts, note the source.

2. **Accessibility**:
   - Each chapter should be 1500-3000 words
   - Use short paragraphs (3-5 sentences)
   - Include visual elements to break up text

3. **Progressive Learning**: Ensure each chapter builds on previous knowledge and prepares for future topics.

4. **Consistency**: Maintain consistent formatting, terminology, and style across all chapters.

### Diagram and Visual Standards

1. **ASCII Diagrams**: Use simple ASCII characters for diagrams that will be converted to graphics later
2. **Placeholder Descriptions**: Provide detailed descriptions for diagrams that will be created separately
3. **Figure Captions**: Always include descriptive captions that explain what the figure shows

### Cross-References

1. **Internal Links**: Use Docusaurus-style internal links when referencing other chapters:
   ```
   [See Chapter X for more details](./chapter-x-link.md)
   ```

2. **Section References**: When referencing sections within the same chapter, use descriptive text rather than numbers since sections may be reorganized.