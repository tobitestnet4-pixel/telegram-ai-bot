# Railway Bot Deployment Automation Script
# This script automates the entire Railway deployment process

Write-Host "🚀 Railway Bot Deployment Automation" -ForegroundColor Cyan
Write-Host "====================================`n" -ForegroundColor Cyan

# Step 1: Install Railway CLI
Write-Host "📦 Step 1: Installing Railway CLI..." -ForegroundColor Yellow
npm install -g @railway/cli
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install Railway CLI. Make sure Node.js/npm is installed." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Railway CLI installed`n" -ForegroundColor Green

# Step 2: Check if user is logged in
Write-Host "🔐 Step 2: Railway Authentication" -ForegroundColor Yellow
Write-Host "You will be redirected to railway.app to log in." -ForegroundColor Cyan
Write-Host "Press Enter to continue..." -ForegroundColor Gray
Read-Host

railway login
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Authentication failed. Please try again." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Successfully authenticated`n" -ForegroundColor Green

# Step 3: Link to project
Write-Host "🔗 Step 3: Linking to Your Project" -ForegroundColor Yellow
Write-Host "Opening Railway to select your telegram-ai-bot project..." -ForegroundColor Cyan
Write-Host "Press Enter to continue..." -ForegroundColor Gray
Read-Host

railway link
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to link project. Make sure telegram-ai-bot exists on Railway." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Successfully linked to project`n" -ForegroundColor Green

# Step 4: Set environment variables
Write-Host "⚙️  Step 4: Setting Environment Variables" -ForegroundColor Yellow

$telegramToken = "8740139600:AAEGJuDz1Fcaf-STLXZlO0eeAdN9lWNY5HY"
$openaiKey = "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"

Write-Host "Setting TELEGRAM_BOT_TOKEN..." -ForegroundColor Cyan
railway variables set TELEGRAM_BOT_TOKEN "$telegramToken"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to set TELEGRAM_BOT_TOKEN" -ForegroundColor Red
    exit 1
}
Write-Host "✅ TELEGRAM_BOT_TOKEN set`n" -ForegroundColor Green

Write-Host "Setting OPENAI_API_KEY..." -ForegroundColor Cyan
railway variables set OPENAI_API_KEY "$openaiKey"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to set OPENAI_API_KEY" -ForegroundColor Red
    exit 1
}
Write-Host "✅ OPENAI_API_KEY set`n" -ForegroundColor Green

# Step 5: Verify variables
Write-Host "🔍 Step 5: Verifying Variables" -ForegroundColor Yellow
railway variables
Write-Host "`n"

# Step 6: Deploy
Write-Host "🚀 Step 6: Deploying Your Bot" -ForegroundColor Yellow
Write-Host "This will start your bot on Railway..." -ForegroundColor Cyan
railway up
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Deployment initiated. Check Railway dashboard for status." -ForegroundColor Yellow
}

Write-Host "`n" 
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "====================================`n" -ForegroundColor Green
Write-Host "Your bot is now live on Railway! 🎉" -ForegroundColor Cyan
Write-Host "`nTo monitor your bot:" -ForegroundColor Yellow
Write-Host "  1. Go to https://railway.app" -ForegroundColor Gray
Write-Host "  2. Select your telegram-ai-bot project" -ForegroundColor Gray
Write-Host "  3. Check the 'Logs' tab for real-time status" -ForegroundColor Gray
Write-Host "`nTo make updates:" -ForegroundColor Yellow
Write-Host "  1. Edit your bot in Visual Studio" -ForegroundColor Gray
Write-Host "  2. Commit: git add . && git commit -m 'Your message'" -ForegroundColor Gray
Write-Host "  3. Push: git push origin main" -ForegroundColor Gray
Write-Host "  4. Railway auto-deploys within 2 minutes" -ForegroundColor Gray
