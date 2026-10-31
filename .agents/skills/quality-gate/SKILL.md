---
name: quality-gate
description: |
  產出前品質閘門。對應 app/quality_gate.py、mcp_verification、forbidden_conclusions。
---

# 品質閘門

檢查：法源是否有 MCP 紀錄或 [待檢索]；是否自動定罪用語；草稿標註；citation 可追溯；MCP status 非假 VERIFIED。
不通過則補 MCP 或改寫後再交。
