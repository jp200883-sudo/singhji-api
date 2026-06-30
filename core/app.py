from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import importlib.util,sys,inspect,os
from pathlib import Path

app=FastAPI(title="Singh Ji AI Ultra v7.0",version="7.0.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])

MODULES={};loaded=[];failed={}

def auto_handler(name,mod):
    def h(data=None):
        funcs={n:f for n,f in vars(mod).items() if callable(f) and not n.startswith('_')}
        for n,f in funcs.items():
            if n not in ('handler','Handler'):
                try:
                    import inspect as ins
                    return {"module":name,"status":"success","data":f(data) if len(ins.signature(f).parameters)>0 else f()}
                except:return {"module":name,"status":"error","error":"function failed"}
        return {"module":name,"status":"success","message":name+" active!"}
    return h

def load(name):
    p=Path("modules")/name;info={"name":name,"handler":None,"status":"loading"}
    try:
        if p.is_dir():
            t=p/"__init__.py" if (p/"__init__.py").exists() else p/"handler.py"
            if not t.exists():info["status"]="not_found";return info
            s=importlib.util.spec_from_file_location("m."+name,str(t))
        elif p.suffix==".py":
            s=importlib.util.spec_from_file_location("m."+name,str(p))
        else:info["status"]="not_found";return info
        m=importlib.util.module_from_spec(s);sys.modules["m."+name]=m;s.loader.exec_module(m)
        h=getattr(m,"handler",getattr(m,"Handler",None))
        info["handler"]=h if h else auto_handler(name,m)
        info["status"]="loaded";print("✅ "+name)
    except Exception as e:info["status"]="error";info["error"]=str(e);print("❌ "+name+": "+str(e))
    return info

print("🚀 Starting...");mp=Path("modules")
if mp.exists():
    for i in mp.iterdir():
        n=i.stem if i.is_file() else i.name
        if n.startswith("_") or (i.is_file() and i.suffix!=".py"):continue
        x=load(n);MODULES[n]=x
        if x["status"]=="loaded":loaded.append(n)
        else:failed[n]=x.get("error","?")
print("✅ Loaded: "+str(len(loaded))+"/"+str(len(MODULES)))

@app.post("/api/{m}")
@app.get("/api/{m}")
async def api(m:str,request:Request):
    if m not in MODULES or MODULES[m]["status"]!="loaded":return JSONResponse(status_code=404,content={"error":"Not found"})
    h=MODULES[m].get("handler")
    if not h:return JSONResponse(status_code=500,content={"error":"No handler"})
    try:d=await request.json() if request.method=="POST" else dict(request.query_params)
    except:d={}
    try:return JSONResponse(content=h(d))
    except Exception as e:return JSONResponse(status_code=500,content={"error":str(e)})

@app.get("/api/health")
def health():return{"status":"🦁 LIVE","loaded":len(loaded),"total":len(MODULES)}
@app.get("/api/status")
def status():return{"loaded":len(loaded),"failed":len(failed),"modules":loaded}
@app.get("/")
def root():return{"name":"Singh Ji AI Ultra v7.0","modules":len(loaded)}

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
