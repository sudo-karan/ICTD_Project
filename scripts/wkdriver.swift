// A small driver for WebKit - the engine Safari uses - with nothing but the system frameworks. It hosts one WKWebView in a
// window placed off the screen, takes one JSON command per line on standard input and answers with one JSON line:
//   {"op":"open","url":"file:///...","dir":"/folder/the/page/may/read"}   -> {"ok":true}
//   {"op":"js","code":"<expression that yields a string>"}               -> {"ok":true,"value":"..."}
//   {"op":"shot","path":"/where/to/write.png"}                           -> {"ok":true}
//   {"op":"size","w":820,"h":600}                                        -> {"ok":true}
//   {"op":"quit"}
// It touches no browser, profile or setting. _browser_webkit.py builds it: swiftc -O wkdriver.swift -o <temporary file>
import Cocoa
import WebKit

final class Driver: NSObject, WKNavigationDelegate {
    let web: WKWebView
    let window: NSWindow
    var loaded: ((Bool, String) -> Void)?

    override init() {
        let cfg = WKWebViewConfiguration()
        // The view lies off the screen, where WebKit calls the page hidden and gives it no animation frames. So frames are
        // given by a timer instead: without them the map library would never redraw. Nothing else of the page is changed.
        let catcher = "window.__errors = []; window.addEventListener('error', function (e) { window.__errors.push(String(e.message) + ' @' + e.lineno); });"
            + " window.requestAnimationFrame = function (f) { return setTimeout(function () { f(performance.now()); }, 16); }; window.cancelAnimationFrame = function (i) { clearTimeout(i); };"
        cfg.userContentController.addUserScript(WKUserScript(source: catcher, injectionTime: .atDocumentStart, forMainFrameOnly: true))
        let frame = NSRect(x: 0, y: 0, width: 1500, height: 950)
        web = WKWebView(frame: frame, configuration: cfg)
        window = NSWindow(contentRect: NSRect(x: -4000, y: -4000, width: 1500, height: 950), styleMask: [.borderless], backing: .buffered, defer: false)
        super.init()
        web.navigationDelegate = self
        window.contentView = web
        window.orderFrontRegardless()          // "in front" of nothing: it lies off the screen; a window that is not ordered in draws no frames
    }
    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) { loaded?(true, ""); loaded = nil }
    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) { loaded?(false, error.localizedDescription); loaded = nil }
    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) { loaded?(false, error.localizedDescription); loaded = nil }
}

func reply(_ obj: [String: Any]) {
    let data = try! JSONSerialization.data(withJSONObject: obj, options: [])
    FileHandle.standardOutput.write(data)
    FileHandle.standardOutput.write("\n".data(using: .utf8)!)
}

let app = NSApplication.shared
app.setActivationPolicy(.accessory)
let driver = Driver()

func handle(_ line: String) {
    guard let data = line.data(using: .utf8), let cmd = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any], let op = cmd["op"] as? String else {
        reply(["ok": false, "error": "not a command"]); return
    }
    switch op {
    case "open":
        guard let s = cmd["url"] as? String, let url = URL(string: s) else { reply(["ok": false, "error": "bad url"]); return }
        driver.loaded = { ok, err in reply(["ok": ok, "error": err]) }
        if url.isFileURL, let dir = cmd["dir"] as? String {
            driver.web.loadFileURL(url, allowingReadAccessTo: URL(fileURLWithPath: dir, isDirectory: true))
        } else {
            driver.web.load(URLRequest(url: url))
        }
    case "js":
        driver.web.evaluateJavaScript(cmd["code"] as? String ?? "") { value, error in
            if let error = error { reply(["ok": false, "error": String(describing: error)]) }
            else { reply(["ok": true, "value": value as? String ?? (value.map { String(describing: $0) } ?? "")]) }
        }
    case "shot":
        let cfg = WKSnapshotConfiguration()
        driver.web.takeSnapshot(with: cfg) { image, error in
            guard let image = image, let tiff = image.tiffRepresentation, let rep = NSBitmapImageRep(data: tiff), let png = rep.representation(using: .png, properties: [:]) else {
                reply(["ok": false, "error": String(describing: error)]); return
            }
            do { try png.write(to: URL(fileURLWithPath: cmd["path"] as? String ?? "/dev/null")); reply(["ok": true, "width": rep.pixelsWide, "height": rep.pixelsHigh]) }
            catch { reply(["ok": false, "error": String(describing: error)]) }
        }
    case "size":
        let w = cmd["w"] as? Int ?? 1500, h = cmd["h"] as? Int ?? 950
        driver.window.setContentSize(NSSize(width: w, height: h))
        driver.web.frame = NSRect(x: 0, y: 0, width: w, height: h)
        reply(["ok": true])
    case "quit":
        reply(["ok": true]); exit(0)
    default:
        reply(["ok": false, "error": "unknown op"])
    }
}

DispatchQueue.global().async {
    while let line = readLine() {
        DispatchQueue.main.async { handle(line) }
    }
    DispatchQueue.main.async { exit(0) }
}
app.run()
