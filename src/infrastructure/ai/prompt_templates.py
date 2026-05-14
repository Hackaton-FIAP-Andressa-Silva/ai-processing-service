SYSTEM_PROMPT = """You are a senior software architect with deep expertise in distributed systems, 
microservices, cloud architecture, and security. 
Your task is to analyze architecture diagrams and provide structured technical analysis.
You MUST respond ONLY with valid JSON. Do not include any text, markdown, or explanation outside the JSON structure.
"""

USER_PROMPT_TEMPLATE = """Analyze this software architecture diagram and provide a comprehensive technical assessment.

You MUST respond with ONLY this exact JSON structure (no other text):
{{
  "summary": "2-3 sentence overview of the architecture",
  "components": [
    {{
      "name": "component name",
      "type": "one of: API, Database, Queue, Cache, Service, Gateway, CDN, LoadBalancer, Storage, Frontend, External",
      "description": "what this component does",
      "technology": "identified technology or 'Not identified'"
    }}
  ],
  "risks": [
    {{
      "title": "risk title",
      "severity": "HIGH or MEDIUM or LOW",
      "description": "detailed description of the risk",
      "impact": "potential business/technical impact",
      "affected_components": ["component name 1", "component name 2"]
    }}
  ],
  "recommendations": [
    {{
      "title": "recommendation title",
      "priority": "HIGH or MEDIUM or LOW",
      "description": "what to implement",
      "rationale": "why this improvement is important"
    }}
  ]
}}

Rules:
- Identify ALL visible components in the diagram
- Include at least 1 risk and 1 recommendation
- severity and priority MUST be exactly "HIGH", "MEDIUM", or "LOW" (uppercase)
- Do not invent components that are not visible in the diagram
- If the image is not an architecture diagram, set summary to "Not an architecture diagram" and return empty arrays
"""
