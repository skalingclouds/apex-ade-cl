# Product Requirement Prompt (PRP) Framework

## What is a PRP?

A **Product Requirement Prompt (PRP)** is a comprehensive, structured document that translates product requirements into actionable prompts for AI agents. It serves as a bridge between human product vision and AI-driven implementation.

## Key Components

### 1. **Context Definition**
- Product overview and vision
- Target users and personas
- Business objectives and success metrics
- Technical constraints and requirements

### 2. **Feature Specification**
- Detailed feature descriptions
- User stories and acceptance criteria
- Technical implementation requirements
- UI/UX specifications

### 3. **Agent Instructions**
- Clear, actionable tasks for AI agents
- Step-by-step implementation guidance
- Quality assurance criteria
- Integration requirements

### 4. **Research & References**
- Market research and competitive analysis
- Technical documentation links
- Design references and mockups
- Best practices and patterns

## Why Use PRPs?

1. **Consistency**: Ensures all AI agents work from the same comprehensive understanding
2. **Clarity**: Reduces ambiguity in requirements and implementation details
3. **Efficiency**: Streamlines the development process by providing complete context upfront
4. **Quality**: Includes built-in quality criteria and validation steps
5. **Scalability**: Can be reused and adapted for similar features

## PRP Creation Process

1. **Research Phase**
   - Gather all relevant information
   - Analyze similar products/features
   - Identify technical requirements
   - Define success criteria

2. **Structuring Phase**
   - Organize information into PRP template sections
   - Create clear user stories
   - Define technical specifications
   - Establish quality metrics

3. **Validation Phase**
   - Review for completeness
   - Ensure clarity and actionability
   - Validate technical feasibility
   - Confirm alignment with business goals

4. **Refinement Phase**
   - Iterate based on feedback
   - Add missing details
   - Clarify ambiguous requirements
   - Optimize for AI comprehension

## Best Practices

- **Be Specific**: Provide concrete examples and detailed specifications
- **Include Context**: Always explain the "why" behind requirements
- **Define Success**: Clear acceptance criteria and quality metrics
- **Consider Edge Cases**: Address potential issues and exceptions
- **Provide References**: Include mockups, diagrams, and documentation links
- **Use Clear Language**: Write for both human and AI understanding

## PRP vs Traditional Requirements

| Traditional PRD | PRP |
|----------------|-----|
| Human-focused | AI-agent optimized |
| High-level requirements | Detailed implementation guidance |
| Separate technical specs | Integrated technical details |
| Static document | Living, actionable prompt |
| Linear structure | Multi-dimensional context |

## Getting Started

1. Use the `base_template_v1` as your starting point
2. Customize sections based on your specific needs
3. Ensure all critical information is captured
4. Review with stakeholders before implementation
5. Iterate and improve based on results

## Directory Structure

```
concept_library/cc_PRP_flow/
├── README.md (this file)
├── PRPs/
│   ├── base_template_v1
│   └── [your_prp_name]
└── examples/
    └── [example_prps]
```