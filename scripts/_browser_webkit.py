"""Python side of wkdriver.swift (WebKit, the engine Safari uses): open a page from disk, run script in it, take
snapshots. Events here are DOM events dispatched in the page - a click() on a control, a MouseEvent on the map - not
operating system input: WebKit off the screen takes no mouse. What that does and does not show is said in docs/LAYER.md.
The driver is compiled from wkdriver.swift the first time it is needed (swiftc, macOS only) into the temporary folder;
no binary is kept in the repository."""
import hashlib, json, shutil, subprocess, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "wkdriver.swift"


def driver():
    """The compiled driver for this source: built once for each version of the source."""
    binary = Path(tempfile.gettempdir()) / ("ictd_wkdriver_" + hashlib.sha256(SOURCE.read_bytes()).hexdigest()[:16])
    if not binary.exists():
        if not shutil.which("swiftc"):
            raise RuntimeError("swiftc is not on this machine: the WebKit check needs macOS with the Swift compiler")
        r = subprocess.run(["swiftc", "-O", str(SOURCE), "-o", str(binary)], capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError("wkdriver.swift did not compile:\n" + r.stderr[-2000:])
    return binary


class WebKit:
    def __init__(self):
        self.p = subprocess.Popen([str(driver())], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)

    def _cmd(self, **c):
        self.p.stdin.write(json.dumps(c) + "\n")
        self.p.stdin.flush()
        line = self.p.stdout.readline()
        if not line:
            raise RuntimeError("the WebKit driver ended")
        r = json.loads(line)
        if not r.get("ok"):
            raise RuntimeError(f"{c.get('op')}: {r.get('error')}")
        return r

    def js(self, expression):
        """The value of a JavaScript expression in the page (anything JSON can carry)."""
        r = self._cmd(op="js", code="JSON.stringify((function(){ return (" + expression + "); })())")
        return json.loads(r["value"]) if r["value"] not in ("", "undefined") else None

    def run(self, statements):
        self._cmd(op="js", code="(function(){ " + statements + " })(); 'done'")

    def open(self, url, folder, ready="window.ICTD_READY === true", wait_s=120):
        self._cmd(op="open", url=url, dir=folder)
        t0 = time.time()
        while time.time() - t0 < wait_s:
            time.sleep(0.5)
            try:
                if self.js(ready):
                    time.sleep(1.5)
                    return round(time.time() - t0, 1)
            except RuntimeError:
                pass
        raise RuntimeError("the page was not ready in WebKit after %d s" % wait_s)

    def shot(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        time.sleep(0.4)
        return self._cmd(op="shot", path=str(path))

    def size(self, w, h):
        self._cmd(op="size", w=w, h=h)
        time.sleep(1.0)

    def close(self):
        try:
            self._cmd(op="quit")
        except Exception:
            pass
        try:
            self.p.wait(timeout=5)
        except Exception:
            self.p.kill()
