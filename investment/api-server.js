const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = 3000;
const REPORTS_DIR = '/home/ubuntu/friday/web/reports';

// 报告元数据映射（用于显示标题和描述）
const reportMeta = {
    'unh_dcf_valuation_2026-02-11.html': {
        icon: '🏥',
        title: '联合健康(UNH) DCF估值',
        meta: '监管风暴下的价值重置 | 目标价 $398.50 | 买入评级'
    },
    'pdd_dcf_valuation_2026-02-11.html': {
        icon: '🛒',
        title: '拼多多(PDD) DCF估值',
        meta: '全球化扩张与Temu韧性 | 目标价 $154 | 优于大盘'
    },
    'msft_dcf_valuation_2026-02-11.html': {
        icon: '📊',
        title: 'MSFT DCF估值分析',
        meta: '微软公司现金流折现估值 | 内在价值 $369.50'
    },
    'us_stock_main_theme_2026-02-11.html': {
        icon: '🇺🇸',
        title: '美股主线标的分析',
        meta: 'AI资本回报率审视 · 行业轮动 · 六只精选标的'
    },
    'davis_double_play_2026-02-11.html': {
        icon: '🎯',
        title: '戴维斯双击扫描',
        meta: '7只潜力标的 | 美光(MU)、阿里(9988.HK)等'
    },
    'investment_logic_2026-02-11.html': {
        icon: '🧠',
        title: '投资逻辑分析',
        meta: '美股·港股·黄金·BTC | 策略权重与风险评估'
    }
};

// 扫描报告目录
function scanReports() {
    try {
        const files = fs.readdirSync(REPORTS_DIR);
        const reports = [];
        
        files.forEach(file => {
            if (file.endsWith('.html') && file !== 'index.html') {
                const stat = fs.statSync(path.join(REPORTS_DIR, file));
                const dateMatch = file.match(/(\d{4}-\d{2}-\d{2})/);
                const date = dateMatch ? dateMatch[1] : stat.mtime.toISOString().split('T')[0];
                
                // 尝试从文件内容提取标题
                let title = file.replace('.html', '');
                let meta = '投资研究报告';
                let icon = '📄';
                
                // 使用预定义元数据或尝试从文件读取
                if (reportMeta[file]) {
                    title = reportMeta[file].title;
                    meta = reportMeta[file].meta;
                    icon = reportMeta[file].icon;
                } else {
                    // 尝试读取文件标题
                    try {
                        const content = fs.readFileSync(path.join(REPORTS_DIR, file), 'utf8');
                        const titleMatch = content.match(/<title>(.+?)<\/title>/);
                        if (titleMatch) {
                            title = titleMatch[1].split('|')[0].trim();
                        }
                        const h1Match = content.match(/<h1>(.+?)<\/h1>/);
                        if (h1Match && title === file.replace('.html', '')) {
                            title = h1Match[1].replace(/<[^>]+>/g, '').trim();
                        }
                    } catch (e) {}
                }
                
                reports.push({
                    file: file,
                    title: title,
                    meta: meta,
                    icon: icon,
                    date: date,
                    mtime: stat.mtime
                });
            }
        });
        
        // 按修改时间倒序
        return reports.sort((a, b) => b.mtime - a.mtime);
    } catch (err) {
        console.error('扫描报告目录失败:', err);
        return [];
    }
}

const server = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;
    
    // CORS 头
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }
    
    // API: 获取报告列表
    if (pathname === '/api/reports') {
        const reports = scanReports();
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            success: true,
            count: reports.length,
            reports: reports
        }));
        return;
    }
    
    // 健康检查
    if (pathname === '/health') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'ok', time: new Date().toISOString() }));
        return;
    }
    
    // 404
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Not found' }));
});

server.listen(PORT, '127.0.0.1', () => {
    console.log(`报告API服务运行在 http://127.0.0.1:${PORT}`);
    console.log('可用端点:');
    console.log(`  - http://127.0.0.1:${PORT}/api/reports  (获取报告列表)`);
    console.log(`  - http://127.0.0.1:${PORT}/health       (健康检查)`);
});