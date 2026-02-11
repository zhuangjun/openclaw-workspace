import Cocoa
import WebKit

@main
class AppDelegate: NSObject, NSApplicationDelegate {
    var statusItem: NSStatusItem!
    var browserWindow: NSWindow?
    var webView: WKWebView?
    
    // 任务队列
    var taskQueue: [ResearchTask] = []
    var isRunning = false
    
    struct ResearchTask {
        let name: String
        let query: String
        let outputPath: String
    }
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        // 创建菜单栏图标
        statusItem = NSStatusBar.shared.statusItem(withLength: NSStatusItem.variableLength)
        statusItem.button?.title = "🤖"
        
        let menu = NSMenu()
        menu.addItem(NSMenuItem(title: "状态: 待机", action: nil, keyEquivalent: ""))
        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "启动浏览器", action: #selector(showBrowser), keyEquivalent: "b"))
        menu.addItem(NSMenuItem(title: "执行 Deep Research", action: #selector(runResearch), keyEquivalent: "r"))
        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "查看队列", action: #selector(showQueue), keyEquivalent: "q"))
        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "退出", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q"))
        
        statusItem.menu = menu
        
        // 启动时自动显示浏览器
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            self.showBrowser()
        }
        
        // 每分钟检查任务队列
        Timer.scheduledTimer(withTimeInterval: 60, repeats: true) { _ in
            self.checkQueue()
        }
        
        print("✅ Gemini 自动化助手已启动")
    }
    
    @objc func showBrowser() {
        if browserWindow == nil {
            let window = NSWindow(
                contentRect: NSRect(x: 0, y: 0, width: 1280, height: 800),
                styleMask: [.titled, .closable, .miniaturizable, .resizable],
                backing: .buffered,
                defer: false
            )
            window.title = "Gemini Deep Research"
            window.center()
            
            // 创建 WebView
            let webView = WKWebView(frame: window.contentView!.bounds)
            webView.autoresizingMask = [.width, .height]
            window.contentView?.addSubview(webView)
            
            // 加载 Gemini
            let request = URLRequest(url: URL(string: "https://gemini.google.com/app")!)
            webView.load(request)
            
            self.webView = webView
            browserWindow = window
        }
        
        browserWindow?.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
        
        updateStatus("浏览器已打开，请登录")
    }
    
    @objc func runResearch() {
        // 这里可以通过 AppleScript 或 JavaScript 注入来操作 WebView
        // 执行 Deep Research 流程
        
        let script = """
        (function() {
            // 找到输入框并输入
            const input = document.querySelector('[contenteditable="true"]');
            if (input) {
                input.innerHTML = '请生成股市综合晨报，日期为 2026年2月11日';
                // 触发输入事件
                input.dispatchEvent(new Event('input', { bubbles: true }));
                return '已输入';
            }
            return '未找到输入框';
        })();
        """
        
        webView?.evaluateJavaScript(script) { result, error in
            if let error = error {
                print("❌ JS 错误: \(error)")
            } else {
                print("✅ JS 结果: \(String(describing: result))")
            }
        }
    }
    
    @objc func showQueue() {
        let alert = NSAlert()
        alert.messageText = "任务队列"
        alert.informativeText = taskQueue.isEmpty ? "队列为空" : "\(taskQueue.count) 个任务等待中"
        alert.alertStyle = .informational
        alert.addButton(withTitle: "确定")
        alert.runModal()
    }
    
    func checkQueue() {
        guard !taskQueue.isEmpty, !isRunning else { return }
        
        // 检查 WebView 是否准备好
        guard let webView = webView else {
            showBrowser()
            return
        }
        
        // 执行队列中的第一个任务
        let task = taskQueue.removeFirst()
        executeTask(task)
    }
    
    func executeTask(_ task: ResearchTask) {
        isRunning = true
        updateStatus("正在执行: \(task.name)")
        
        // 使用 JavaScript 注入来操作 Gemini
        // 这里可以实现完整的 Deep Research 流程
        
        print("▶️ 执行任务: \(task.name)")
        
        // 模拟完成
        DispatchQueue.main.asyncAfter(deadline: .now() + 5) {
            self.isRunning = false
            self.updateStatus("待机")
            print("✅ 任务完成: \(task.name)")
        }
    }
    
    func updateStatus(_ status: String) {
        DispatchQueue.main.async {
            self.statusItem.menu?.item(at: 0)?.title = "状态: \(status)"
        }
    }
}

// 主函数
let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
