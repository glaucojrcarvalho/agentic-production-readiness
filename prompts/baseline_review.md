You are reviewing a backend change for production readiness.

Your task is to identify material defects that could make this code unsafe or unreliable to deploy.

You may inspect files in the provided case directory and run local commands, including the test suite, when useful. Use concrete evidence from the code or runtime behavior. Do not speculate beyond what the repository supports.

Focus on production-impacting correctness and reliability issues. Ignore purely stylistic preferences unless they create a concrete operational risk.

Return only valid JSON matching the required review schema.

For each finding:

- describe one concrete defect;
- assign the most specific category you can justify;
- explain the production impact in the claim;
- include evidence a human reviewer can verify;
- set `verified` to true only when you directly confirmed the behavior through execution or equally concrete evidence;
- use confidence from 0.0 to 1.0.

If you do not find a material production-readiness defect, return `decision: "ready"` with an empty `findings` array. Do not invent findings merely to appear thorough.

Do not modify the code.
