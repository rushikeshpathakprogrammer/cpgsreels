"""Generate voice lines with Sarvam Bulbul v3.
Usage: python engine/tts.py jobs/<job>.json
Job file: {"name": "reel001", "lines": [{"id": "01", "speaker": "shubh", "text": "...", "pace": 1.1}]}
Writes audio/<name>/<id>.wav and audio/<name>/report.json
"""
import base64, json, os, sys, time, urllib.request, urllib.error

KEY = os.environ.get("SARVAM_API_KEY", "").strip()
URL = "https://api.sarvam.ai/text-to-speech"

def call(payload):
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(), method="POST",
        headers={"api-subscription-key": KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())

def main(job_path):
    if not KEY:
        sys.exit("SARVAM_API_KEY secret is missing")
    job = json.load(open(job_path, encoding="utf-8"))
    out = os.path.join("audio", job["name"]); os.makedirs(out, exist_ok=True)
    report = []
    for ln in job["lines"]:
        payload = {"text": ln["text"], "target_language_code": ln.get("lang", "hi-IN"),
                   "speaker": ln["speaker"], "model": job.get("model", "bulbul:v3"),
                   "pace": ln.get("pace", 1.0), "speech_sample_rate": 24000}
        if "temperature" in ln: payload["temperature"] = ln["temperature"]
        for attempt in range(3):
            try:
                res = call(payload); break
            except urllib.error.HTTPError as e:
                body = e.read().decode(errors="replace")
                print("HTTP", e.code, body[:500])
                if e.code in (429, 500, 502, 503) and attempt < 2: time.sleep(5); continue
                report.append({"id": ln["id"], "error": f"{e.code} {body[:300]}"}); res = None; break
        if not res: continue
        audio = base64.b64decode("".join(res["audios"]))
        open(os.path.join(out, ln["id"] + ".wav"), "wb").write(audio)
        report.append({"id": ln["id"], "bytes": len(audio)}); print("ok", ln["id"], len(audio))
    json.dump(report, open(os.path.join(out, "report.json"), "w"), indent=1)
    if any("error" in r for r in report): sys.exit("some lines failed: see report.json")

if __name__ == "__main__":
    main(sys.argv[1])
