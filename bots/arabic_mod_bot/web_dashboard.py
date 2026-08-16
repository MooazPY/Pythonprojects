"""
Web Dashboard & Status Inspector for Haris Pro.

Lightweight, zero-dependency async HTTP server running alongside Discord bot.
Provides live web telemetry, security metrics, and interactive API endpoints.
"""

from __future__ import annotations

import logging
import os
import json
from typing import TYPE_CHECKING
from aiohttp import web

if TYPE_CHECKING:
    from main import HarisBot

logger = logging.getLogger("haris.web_dashboard")

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Haris Pro — لوحة التحكم والأمان</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0f172a;
            --card-bg: #1e293b;
            --accent: #6366f1;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --success: #10b981;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Tajawal', sans-serif; }
        body { background-color: var(--bg-dark); color: var(--text-main); min-height: 100vh; padding: 2rem; }

        .container { max-width: 1200px; margin: 0 auto; }
        
        header {
            display: flex; justify-content: space-between; align-items: center;
            background: var(--card-bg); padding: 1.5rem 2rem; border-radius: 16px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3); margin-bottom: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .brand { display: flex; align-items: center; gap: 1rem; }
        .brand-icon { font-size: 2.5rem; }
        .brand-title h1 { font-size: 1.5rem; font-weight: 900; background: linear-gradient(135deg, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .brand-title p { font-size: 0.875rem; color: var(--text-muted); }

        .status-badge {
            display: flex; align-items: center; gap: 0.5rem; background: rgba(16, 185, 129, 0.1);
            color: var(--success); padding: 0.5rem 1rem; border-radius: 9999px; border: 1px solid rgba(16, 185, 129, 0.2);
            font-weight: 700; font-size: 0.875rem;
        }
        .status-dot { width: 10px; height: 10px; background: var(--success); border-radius: 50%; animation: pulse 2s infinite; }

        @keyframes pulse { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(1.2); } 100% { opacity: 1; transform: scale(1); } }

        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }

        .card {
            background: var(--card-bg); padding: 1.5rem; border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.05); transition: transform 0.2s, box-shadow 0.2s;
        }
        .card:hover { transform: translateY(-4px); box-shadow: 0 15px 30px -5px rgba(0, 0, 0, 0.4); }

        .card-header { display: flex; justify-content: space-between; align-items: center; color: var(--text-muted); margin-bottom: 1rem; }
        .card-value { font-size: 2.25rem; font-weight: 900; color: var(--text-main); }
        .card-subtext { font-size: 0.85rem; color: var(--text-muted); margin-top: 0.5rem; }

        .panel {
            background: var(--card-bg); padding: 2rem; border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .panel-title { font-size: 1.25rem; font-weight: 700; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem; }

        .info-table { width: 100%; border-collapse: collapse; }
        .info-table th, .info-table td { text-align: right; padding: 1rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
        .info-table th { color: var(--text-muted); font-weight: 500; }
        .info-table td { font-weight: 700; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="brand">
                <div class="brand-icon">🛡️</div>
                <div class="brand-title">
                    <h1>حارس Pro — Haris Security Dashboard</h1>
                    <p>لوحة الحماية والتحليل الذكي المباشر</p>
                </div>
            </div>
            <div class="status-badge">
                <span class="status-dot"></span>
                <span>النظام يعمل بنجاح (Online)</span>
            </div>
        </header>

        <div class="grid">
            <div class="card">
                <div class="card-header"><span>🌐 السيرفرات النشطة</span><span>🏰</span></div>
                <div class="card-value" id="guildsCount">-</div>
                <div class="card-subtext">السيرفرات المحمية بواسطة حارس</div>
            </div>
            <div class="card">
                <div class="card-header"><span>🗑️ الرسائل المحذوفة</span><span>⚡</span></div>
                <div class="card-value" id="deletedMessages">-</div>
                <div class="card-subtext">إجمالي المخالفات المكتشفة والـ Auto-Mod</div>
            </div>
            <div class="card">
                <div class="card-header"><span>⚠️ التحذيرات المصدرة</span><span>📜</span></div>
                <div class="card-value" id="warnCount">-</div>
                <div class="card-subtext">إجمالي التحذيرات الموجهة للأعضاء</div>
            </div>
            <div class="card">
                <div class="card-header"><span>🔇 حالات الكتم</span><span>🚫</span></div>
                <div class="card-value" id="muteCount">-</div>
                <div class="card-subtext">حالات الكتم التلقائية المنفذة</div>
            </div>
        </div>

        <div class="panel">
            <div class="panel-title"><span>🤖</span> حالة محرك الذكاء الاصطناعي NLP & Architecture</div>
            <table class="info-table">
                <tr>
                    <th>نموذج الذكاء الاصطناعي</th>
                    <td>CAMeL-Lab DA Sentiment (Hugging Face Router)</td>
                </tr>
                <tr>
                    <th>استجابة الـ Fallback</th>
                    <td>Offline Regex & Evasion Normalizer (Zero-Lag)</td>
                </tr>
                <tr>
                    <th>معالجة التمويه (Arabizi)</th>
                    <td>مفعلة تلقائيًا (الفحص المزدوج Raw + Normalized)</td>
                </tr>
                <tr>
                    <th>قاعدة البيانات المحلية</th>
                    <td>SQLite WAL Mode (Zero Cloud Lag)</td>
                </tr>
            </table>
        </div>
    </div>

    <script>
        async function fetchStats() {
            try {
                const res = await fetch('/api/stats');
                const data = await res.json();
                document.getElementById('guildsCount').textContent = data.active_guilds || 0;
                document.getElementById('deletedMessages').textContent = data.stats_deleted_messages || 0;
                document.getElementById('warnCount').textContent = data.stats_warn_count || 0;
                document.getElementById('muteCount').textContent = data.stats_mute_count || 0;
            } catch (e) {
                console.error('Failed to update stats:', e);
            }
        }
        fetchStats();
        setInterval(fetchStats, 5000);
    </script>
</body>
</html>
"""


class WebDashboardServer:
    def __init__(self, bot: 'HarisBot', port: int = 8080):
        self.bot = bot
        self.port = port
        self.app = web.Application()
        self.runner: web.AppRunner | None = None
        self._setup_routes()

    def _setup_routes(self):
        self.app.router.add_get('/', self.handle_index)
        self.app.router.add_get('/api/stats', self.handle_api_stats)

    async def _check_auth(self, request: web.Request) -> bool:
        required_key = os.environ.get("DASHBOARD_API_KEY", "").strip()
        if not required_key:
            return True  # Auth not required if DASHBOARD_API_KEY environment variable is omitted
        provided_key = request.headers.get("X-API-Key") or request.query.get("key")
        return provided_key == required_key

    async def handle_index(self, request: web.Request) -> web.Response:
        if not await self._check_auth(request):
            return web.Response(text="<h1>401 Unauthorized — Please provide ?key=YOUR_API_KEY</h1>", status=401, content_type='text/html')
        return web.Response(text=DASHBOARD_HTML, content_type='text/html', charset='utf-8')

    async def handle_api_stats(self, request: web.Request) -> web.Response:
        if not await self._check_auth(request):
            return web.json_response({"error": "Unauthorized. Provide X-API-Key header or ?key= query parameter."}, status=401)

        active_guilds = len(self.bot.guilds) if self.bot.is_ready() else 0
        total_deleted = 0
        total_warns = 0
        total_mutes = 0

        try:
            for guild in self.bot.guilds:
                cfg = await self.bot.config_store.get_config(guild.id)
                total_deleted += cfg.stats_deleted_messages
                total_warns += cfg.stats_warn_count
                total_mutes += cfg.stats_mute_count
        except Exception as e:
            logger.debug("Failed to compute aggregate stats: %s", e)

        payload = {
            "status": "online",
            "bot_name": str(self.bot.user) if self.bot.user else "Haris Pro",
            "active_guilds": active_guilds,
            "stats_deleted_messages": total_deleted,
            "stats_warn_count": total_warns,
            "stats_mute_count": total_mutes,
            "ai_model": "CAMeL-Lab/bert-base-arabic-camelbert-da-sentiment",
        }
        return web.json_response(payload)

    async def start(self):
        try:
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            site = web.TCPSite(self.runner, '0.0.0.0', self.port)
            await site.start()
            logger.info("Web Dashboard running on http://0.0.0.0:%d", self.port)
        except Exception as e:
            logger.warning("Failed to start Web Dashboard on port %d: %s", self.port, e)

    async def stop(self):
        if self.runner:
            await self.runner.cleanup()
            logger.info("Web Dashboard server stopped.")

