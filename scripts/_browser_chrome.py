"""A small driver for Chrome over its DevTools protocol, with nothing but the standard library: launch a separate
Chrome with its own empty profile, open a page (file:// works), send real mouse and keyboard events, read the DOM,
take screenshots. Used by exercise_layer.py to exercise 60_layer/index.html control by control. It touches no other
browser and no profile but the empty one it is given."""
import base64, json, os, socket, struct, subprocess, time, urllib.request
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


class WS:
    """A minimal websocket client (RFC 6455): text frames, masking, fragmentation, ping."""
    def __init__(self, url):
        assert url.startswith("ws://")
        host, _, path = url[5:].partition("/")
        h, _, p = host.partition(":")
        self.s = socket.create_connection((h, int(p or 80)), timeout=60)
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((f"GET /{path} HTTP/1.1\r\nHost: {host}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.s.recv(4096)
        if b" 101 " not in buf.split(b"\r\n")[0]:
            raise RuntimeError("websocket handshake refused: " + buf[:200].decode(errors="replace"))
        self.rest = buf.split(b"\r\n\r\n", 1)[1]

    def _read(self, n):
        while len(self.rest) < n:
            chunk = self.s.recv(1 << 16)
            if not chunk:
                raise RuntimeError("websocket closed")
            self.rest += chunk
        out, self.rest = self.rest[:n], self.rest[n:]
        return out

    def send(self, text):
        data = text.encode()
        head = bytearray([0x81])
        n = len(data)
        if n < 126:
            head.append(0x80 | n)
        elif n < 65536:
            head.append(0x80 | 126); head += struct.pack(">H", n)
        else:
            head.append(0x80 | 127); head += struct.pack(">Q", n)
        mask = os.urandom(4)
        self.s.sendall(bytes(head) + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

    def recv(self):
        msg = b""
        while True:
            b0, b1 = self._read(2)
            op, n = b0 & 0x0F, b1 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._read(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._read(8))[0]
            mask = self._read(4) if b1 & 0x80 else None
            data = self._read(n)
            if mask:
                data = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
            if op == 9:                                     # ping -> pong
                self.s.sendall(bytes([0x8A, 0x80]) + os.urandom(4))
                continue
            if op == 8:
                raise RuntimeError("websocket closed by the browser")
            msg += data
            if b0 & 0x80:
                return msg.decode()


class Chrome:
    def __init__(self, profile, port=9333, size=(1500, 950), headless=True):
        self.port, self.n, self.errors = port, 0, []
        Path(profile).mkdir(parents=True, exist_ok=True)
        args = [CHROME, f"--remote-debugging-port={port}", f"--user-data-dir={profile}", f"--window-size={size[0]},{size[1]}", "--no-first-run", "--no-default-browser-check", "--disable-gpu",
                "--remote-allow-origins=*", "--force-device-scale-factor=1", "about:blank"]
        if headless:
            args.insert(1, "--headless=new")
        self.proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(100):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=2))
                page = [t for t in tabs if t.get("type") == "page"]
                if page:
                    break
            except Exception:
                pass
            time.sleep(0.2)
        else:
            raise RuntimeError("Chrome did not open a debugging port")
        self.version = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=5))["Browser"]
        self.ws = WS(page[0]["webSocketDebuggerUrl"])
        for domain in ("Page", "Runtime", "Network", "Log"):
            self.cmd(domain + ".enable")
        self.requests = []

    def cmd(self, method, **params):
        self.n += 1
        mine = self.n
        self.ws.send(json.dumps({"id": mine, "method": method, "params": params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == mine:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m.get("result", {})
            self._event(m)

    def _event(self, m):
        k = m.get("method", "")
        if k == "Runtime.exceptionThrown":
            d = m["params"]["exceptionDetails"]
            self.errors.append((d.get("exception", {}).get("description") or d.get("text", ""))[:300])
        elif k == "Runtime.consoleAPICalled" and m["params"]["type"] in ("error", "warning"):
            self.errors.append("console." + m["params"]["type"] + ": " + " ".join(str(a.get("value", a.get("description", ""))) for a in m["params"]["args"])[:300])
        elif k == "Log.entryAdded" and m["params"]["entry"]["level"] == "error":
            self.errors.append("log: " + m["params"]["entry"]["text"][:300])
        elif k == "Network.requestWillBeSent":
            self.requests.append(m["params"]["request"]["url"])

    def js(self, expression):
        r = self.cmd("Runtime.evaluate", expression=expression, returnByValue=True, awaitPromise=True)
        if "exceptionDetails" in r:
            raise RuntimeError("page script: " + str(r["exceptionDetails"].get("exception", {}).get("description", r["exceptionDetails"]))[:400])
        return r["result"].get("value")

    def open(self, url, ready="window.ICTD_READY === true", wait_s=90):
        self.requests = []
        self.cmd("Page.navigate", url=url)
        t0 = time.time()
        while time.time() - t0 < wait_s:
            time.sleep(0.5)
            try:
                if self.js(ready):
                    time.sleep(1.0)
                    return round(time.time() - t0, 1)
            except RuntimeError:
                pass
        raise RuntimeError(f"the page was not ready after {wait_s} s: {url}")

    def click(self, x, y):
        """A real mouse click at viewport coordinates."""
        for kind in ("mouseMoved", "mousePressed", "mouseReleased"):
            self.cmd("Input.dispatchMouseEvent", type=kind, x=x, y=y, button="none" if kind == "mouseMoved" else "left", buttons=0 if kind != "mousePressed" else 1, clickCount=0 if kind == "mouseMoved" else 1)
        time.sleep(0.35)

    def centre(self, selector, nth=0):
        r = self.js(f"(function(){{var e=document.querySelectorAll({json.dumps(selector)})[{nth}]; if(!e) return null; e.scrollIntoView({{block:'nearest'}}); var b=e.getBoundingClientRect(); return [b.left+b.width/2, b.top+b.height/2, b.width, b.height];}})()")
        if not r or r[2] <= 0 or r[3] <= 0:
            raise RuntimeError(f"nothing to click at {selector} [{nth}]")
        return r[0], r[1]

    def click_on(self, selector, nth=0):
        x, y = self.centre(selector, nth)
        self.click(x, y)
        return round(x), round(y)

    def type(self, text):
        self.cmd("Input.insertText", text=text)

    def key(self, key, code=None, vk=0, text=None):
        for kind in ("keyDown", "keyUp"):
            p = dict(type=kind if text is None or kind == "keyUp" else "keyDown", key=key, code=code or key, windowsVirtualKeyCode=vk, nativeVirtualKeyCode=vk)
            if text is not None and kind == "keyDown":
                p["text"] = text
            self.cmd("Input.dispatchKeyEvent", **p)
        time.sleep(0.3)

    def enter(self):
        self.key("Enter", "Enter", 13, "\r")

    def wheel(self, x, y, dy):
        """Turn the mouse wheel over (x, y): dy > 0 scrolls down (or zooms a map out), dy < 0 up (in). The event is sent
        and its acknowledgement waited for at most three seconds: over some elements headless Chrome sends none."""
        self.cmd("Input.dispatchMouseEvent", type="mouseMoved", x=x, y=y, button="none")
        self.n += 1
        mine = self.n
        self.ws.send(json.dumps({"id": mine, "method": "Input.dispatchMouseEvent", "params": {"type": "mouseWheel", "x": x, "y": y, "deltaX": 0, "deltaY": dy}}))
        self.ws.s.settimeout(3)
        acknowledged = False
        try:
            while True:
                m = json.loads(self.ws.recv())
                if m.get("id") == mine:
                    acknowledged = True
                    break
                self._event(m)
        except (socket.timeout, TimeoutError):
            pass
        self.ws.s.settimeout(60)
        time.sleep(0.8)
        return acknowledged

    def drag(self, x0, y0, x1, y1, steps=8):
        self.cmd("Input.dispatchMouseEvent", type="mouseMoved", x=x0, y=y0, button="none")
        self.cmd("Input.dispatchMouseEvent", type="mousePressed", x=x0, y=y0, button="left", buttons=1, clickCount=1)
        for i in range(1, steps + 1):
            self.cmd("Input.dispatchMouseEvent", type="mouseMoved", x=x0 + (x1 - x0) * i / steps, y=y0 + (y1 - y0) * i / steps, button="left", buttons=1)
            time.sleep(0.03)
        self.cmd("Input.dispatchMouseEvent", type="mouseReleased", x=x1, y=y1, button="left", buttons=0, clickCount=1)
        time.sleep(0.6)

    def shot(self, path):
        data = self.cmd("Page.captureScreenshot", format="png")["data"]
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_bytes(base64.b64decode(data))
        return str(path)

    def close(self):
        try:
            self.cmd("Browser.close")
        except Exception:
            pass
        try:
            self.proc.wait(timeout=10)
        except Exception:
            self.proc.kill()
