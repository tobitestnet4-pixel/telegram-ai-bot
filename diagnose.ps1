# RUN THIS FIRST - Quick Diagnostic
# Copy and paste this entire script into PowerShell

Write-Host "╔════════════════════════════════════════════════╗"
Write-Host "║  TELEGRAM BOT DIAGNOSTIC - QUICK CHECK         ║"
Write-Host "╚════════════════════════════════════════════════╝"

# Check 1: Docker
Write-Host "`n📦 1. CHECKING DOCKER..." -ForegroundColor Cyan
$docker = docker --version 2>$null
if ($docker) {
    Write-Host "   ✅ Docker installed: $docker" -ForegroundColor Green
} else {
    Write-Host "   ❌ Docker NOT running!" -ForegroundColor Red
    Write-Host "   FIX: Install Docker Desktop from https://docker.com" -ForegroundColor Yellow
    exit
}

# Check 2: Docker Compose
Write-Host "`n🐳 2. CHECKING DOCKER COMPOSE..." -ForegroundColor Cyan
$compose = docker-compose --version 2>$null
if ($compose) {
    Write-Host "   ✅ Docker Compose installed" -ForegroundColor Green
} else {
    Write-Host "   ❌ Docker Compose NOT found!" -ForegroundColor Red
    exit
}

# Check 3: .env file
Write-Host "`n🔑 3. CHECKING CREDENTIALS (.env)..." -ForegroundColor Cyan
if (Test-Path ".\.env") {
    $envContent = Get-Content .\.env
    if ($envContent -match "TELEGRAM_BOT_TOKEN") {
        Write-Host "   ✅ TELEGRAM_BOT_TOKEN found" -ForegroundColor Green
    } else {
        Write-Host "   ❌ TELEGRAM_BOT_TOKEN missing!" -ForegroundColor Red
    }
    if ($envContent -match "OPENAI_API_KEY") {
        Write-Host "   ✅ OPENAI_API_KEY found" -ForegroundColor Green
    } else {
        Write-Host "   ❌ OPENAI_API_KEY missing!" -ForegroundColor Red
    }
} else {
    Write-Host "   ❌ .env file not found!" -ForegroundColor Red
}

# Check 4: Required files
Write-Host "`n📄 4. CHECKING REQUIRED FILES..." -ForegroundColor Cyan
$files = @("bot.py", "Dockerfile", "docker-compose.yml", "requirements.txt")
foreach ($file in $files) {
    if (Test-Path ".\$file") {
        Write-Host "   ✅ $file exists" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file missing!" -ForegroundColor Red
    }
}

# Check 5: Is bot already running?
Write-Host "`n🤖 5. CHECKING IF BOT IS RUNNING..." -ForegroundColor Cyan
$running = docker-compose ps 2>$null | Select-String "telegram-ai-bot"
if ($running) {
    Write-Host "   ✅ Bot is RUNNING!" -ForegroundColor Green
    Write-Host "   Status: $running" -ForegroundColor Green
    
    Write-Host "`n   Viewing recent logs (last 10 lines):" -ForegroundColor Cyan
    docker-compose logs --tail 10
} else {
    Write-Host "   ⚠️  Bot is NOT running" -ForegroundColor Yellow
    Write-Host "`n   Quick fix: Run these commands:" -ForegroundColor Cyan
    Write-Host "   1. docker build -t telegram-ai-bot ." -ForegroundColor White
    Write-Host "   2. docker-compose up -d" -ForegroundColor White
    Write-Host "   3. docker-compose logs -f" -ForegroundColor White
}

# Check 6: Summary
Write-Host "`n╔════════════════════════════════════════════════╗"
Write-Host "║  NEXT STEPS                                     ║"
Write-Host "╚════════════════════════════════════════════════╝"
Write-Host ""
Write-Host "If bot is NOT running:" -ForegroundColor Yellow
Write-Host "  1. Run: docker build -t telegram-ai-bot ." -ForegroundColor White
Write-Host "  2. Run: docker-compose up -d" -ForegroundColor White
Write-Host "  3. Run: docker-compose logs -f" -ForegroundColor White
Write-Host "  4. Send message in Telegram" -ForegroundColor White
Write-Host ""
Write-Host "If bot IS running but not responding:" -ForegroundColor Yellow
Write-Host "  1. Check logs: docker-compose logs --tail 50" -ForegroundColor White
Write-Host "  2. Look for error messages (401, 400, 402)" -ForegroundColor White
Write-Host "  3. Check .env credentials are correct" -ForegroundColor White
Write-Host ""
