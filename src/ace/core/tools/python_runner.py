from __future__ import annotations

import time

from ace.core.tool_schemas import ToolError, ToolRequest, ToolResponse


class PythonRunnerTool:
    name="python_runner"
    def run(self,request:ToolRequest)->ToolResponse:
        start=time.time()
        code=str(request.input.get("code","")).strip()
        timeout_ms=int(request.input.get("timeout_ms",800))
        if not code:
            return ToolResponse(
                ok=False,
                name=self.name,
                error=ToolError(code="INVALID_INPUT",message="Missing 'code'"),
                attempts=1,
                duration_ms=int((time.time()-start)*1000),
                
            )
        safe_builtins={
            "abs":abs,
            "min":min,
            "max":max,
            "sum":sum,
            "len":len,
            "range":range,
            "sorted":sorted,
            "round":round,
        }
        globals_dict={"__builtins__":safe_builtins}
        locals_dict:dict[str,object]={}
        t0=time.time()
        try:
            if "import" in code or "__import__" in code:
                raise ValueError("Import statements are not allowed")
            exec(code,globals_dict,locals_dict)
            if (time.time()-t0)*1000>timeout_ms:
                raise TimeoutError("Execution time exceeded")
            result=locals_dict.get("result", None)
            return ToolResponse(
                ok=True,
                name=self.name,
                output={"result":result,"locals":{k.str(v) for k,v in locals_dict.items()}},
                attempts=1,
                duration_ms=int((time.time()-start)*1000), 
            )
        except Exception as exc:
            return ToolResponse(
                ok=False,
                name=self.name,
                error=ToolError(code="RUNTIME_ERROR",message=str(exc)),
                attempts=1,
                duration_ms=int((time.time()-start)*1000),
            )