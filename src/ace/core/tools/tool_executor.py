from __future__ import annotations

import time

from ace.core.tool_schemas import ToolError, ToolRequest, ToolResponse
from ace.core.tools.registry import ToolRegistry


class ToolExecutor:
    def __init__(self, registry:ToolRegistry, max_retries:int=2,backoff_ms:int=150) -> None:
        self.registry = registry
        self.max_retries = max_retries
        self.backoff_ms = backoff_ms
    
    def execute(self,request:ToolRequest) -> ToolResponse:
        attempts=0
        last_resp:ToolResponse | None=None
        while attempts <= self.max_retries:
            attempts+=1
            try:
                tool=self.registry.get(request.name)
                resp=tool.run(request)
                resp.attempts=attempts
                if resp.ok:
                    return resp
                if resp.error and resp.error.code in {"TRANSIENT","TIMEOUT"}:
                    last_resp=resp
                    time.sleep((self.backoff_ms*attempts)/1000.0)
                    continue
                return resp
            except KeyError as exc:
                return ToolResponse(
                    ok=False,
                    name=request.name,
                    error=ToolError(code="UNKNOWN_TOOL",message=str(exc)),
                    attempts=attempts,
                )
            except Exception as exc:
                return ToolResponse(
                    ok=False,
                    name=request.name,
                    error=ToolError(code="EXECUTOR_ERROR",message=str(exc)),
                    attempts=attempts,
                )
                time.sleep((self.backoff_ms*attempts)/1000.0)
        return last_resp or ToolResponse(
            ok=False,
            name=request.name,
            error=ToolError(code="FAILED",message="Tool failed after retries"),
            attempts=attempts,
        )
