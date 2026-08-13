"""Serve the Fialka UI and keep all cipher state in the Python engine."""
from __future__ import annotations
import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from config import ALPHABET, PRESETS
from engine import FialkaEngine
from rotors import HISTORICAL_ROTORS
from configuration_manager import ConfigurationManager

print(">>> USING MY MODIFIED WEB_SERVER.PY <<<")
WEB_ROOT = Path(__file__).resolve().parent
engine = FialkaEngine()

def state():
    return {"alphabet": ALPHABET, "rotor_order": engine.rotors.rotor_order, "positions": engine.rotors.positions,
            "rotors": [{"id": r["id"], "name": r["name"]} for r in HISTORICAL_ROTORS]}

def trace(item):
    if item.get("is_ignored"): return None
    def stage(row): return {"slot":row["slot"],"position":row["position"],"contactIn":row["contact_in"],"wireOut":row["wire_out"],"contactOut":row["contact_out"]}
    return {"inputIndex":item["input_index"],"inputChar":item["input_char"],"forwardRotorPass":[stage(x) for x in item["forward_trace"]],"reflectorEntryIndex":item["reflector_entry"],"reflectorExitIndex":item["reflector_exit"],"reverseRotorPass":[stage(x) for x in item["reverse_trace"]],"outputIndex":item["output_index"],"outputChar":item["output_char"]}

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): 
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)
    def respond(self, value, status=200):
        data=json.dumps(value).encode(); self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_GET(self):

        path = urlparse(self.path).path

        print("=" * 40)
        print("RAW PATH :", self.path)
        print("PARSED   :", path)
        print("=" * 40)

        if path == "/api/state":
            print("Matched STATE")
            self.respond({"state": state()})

        elif path == "/api/configurations":
            print("Matched CONFIGURATIONS")
            self.respond({
                "configurations": ConfigurationManager.list()
            })

        else:
            print("FELL THROUGH")
            super().do_GET()


    def do_POST(self):
        try:
            data=json.loads(self.rfile.read(int(self.headers.get("Content-Length",0))) or b"{}")
            path=urlparse(self.path).path
            if path=="/api/reset": engine.reset_positions(); result={}
            elif path=="/api/preset":
                key=data["preset"]
                if key=="zero": engine.rotors.rotor_order=list(range(10)); engine.reset_positions()
                else: engine.rotors.rotor_order=list(PRESETS[key]["rotor_order"]); engine.rotors.positions=list(PRESETS[key]["positions"])
                result={}
            elif path=="/api/configure":
                slot=int(data["slot"])
                if "rotor" in data: engine.rotors.rotor_order[slot]=int(data["rotor"])
                if "position" in data: engine.rotors.set_position_by_num(slot,int(data["position"]))
                result={}
            elif path=="/api/character":
                item=engine.encipher_char(str(data.get("char", ""))[:1]); result={"output":item["output_char"],"trace":trace(item)}
            elif path=="/api/process":
                output,items=engine.process_text(str(data.get("text", ""))); result={"output":output,"traces":[trace(item) for item in items]}
            elif path == "/api/save_configuration":

                name = str(data["name"]).strip()

                ConfigurationManager.save(engine, name)

                result = {
                   "saved": True
                    }
            elif path == "/api/load_configuration":

               name = str(data["name"]).strip()

               ConfigurationManager.load(engine, name)

               result = {
               "loaded": True
               }

            elif path == "/api/delete_configuration":

                name = str(data["name"]).strip()

                ConfigurationManager.delete(name)

                result = {
                "deleted": True
                }

            else: self.send_error(404); return
            self.respond({"state":state(),**result})
        except (KeyError,ValueError,TypeError,json.JSONDecodeError) as error: self.respond({"error":str(error)},400)

if __name__ == "__main__":
    print("Open http://127.0.0.1:8000")
    ThreadingHTTPServer(("127.0.0.1",8000),Handler).serve_forever()
