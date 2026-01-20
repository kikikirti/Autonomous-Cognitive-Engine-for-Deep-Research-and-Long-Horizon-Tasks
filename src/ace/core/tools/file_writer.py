from __future__ import annotations

import time
from pathlib import Path

from ace.core.tool_schemas import ToolError, ToolRequest, ToolResponse


class FileWriterTool:
    name="file_writer"
    def __init__(self,base_dir:str="artifacts") -> None :
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True,exist_ok=True)
    
    def run(self,request:ToolRequest) -> ToolResponse:
        start=time.time()
        rel_path=str(request.input.get("path","")).strip()
        content=request.input.get("content","")
        if not rel_path:
            return ToolResponse(
                ok=False,
                name=self.name,
                error=ToolError(code="INVALID_INPUT", message="Missing 'path'"),
                attempts=1,
                duration_ms=int((time.time()-start)*1000),
            )
        
        target=(self.base_dir/rel_path).resolve()
        if self.base_dir.resolve() not in target.parents and target != self.base_dir.resolve():
            return ToolResponse(
                ok=False,
                name=self.name,
                error=ToolError(code="SECURITY", message="Path traversal blocked"),
                attempts=1,
                duration_ms=int((time.time()-start)*1000),
            )
        
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(str(content),encoding="utf-8")

        return ToolResponse(
            ok=True,
            name=self.name,
            output={"written_to":str(target),"bytes":len(str(content).encode("utf-8"))},
            attempts=1,
            duration_ms=int((time.time()-start)*1000),
        )
           