# Script to add "Mua tour" button and cart.js to all tour HTML files

$toursJson = Get-Content "F:\Study\Project SItes\tours.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$tourIds = @("10942","11338","13579","18875","18910","18912","18920","18921","18941","18946","18949","18978","19000","19012","19021","19022","19036","19062","19066","19067","19068","19069","19090","19567","19688")

$buttonTemplate = @'
<div style="text-align:center;padding:30px 20px;margin:20px 0;background:#f8f9fa;border-radius:12px;">
  <p style="font-size:22px;font-weight:bold;color:#333;margin-bottom:10px;">GIÁ: {price} VND / khách</p>
  <button onclick="addToCart('{id}','{name}',{priceNum})" style="background:#e74c3c;color:#fff;border:none;padding:15px 40px;font-size:18px;border-radius:8px;cursor:pointer;font-weight:bold;letter-spacing:1px;">🛒 MUA TOUR</button>
</div>
<script src="../scripts/cart.js"></script>
'@

$scriptTag = '<script src="../scripts/cart.js"></script>'

$counter = 0

foreach ($tid in $tourIds) {
    $filePath = "F:\Study\Project SItes\$tid.html"
    if (-not (Test-Path $filePath)) {
        Write-Host "SKIP: $tid.html not found"
        continue
    }
    
    $content = Get-Content $filePath -Raw -Encoding UTF8
    
    # Check if already has the button
    if ($content -match 'addToCart') {
        Write-Host "SKIP: $tid.html already has button"
        continue
    }
    
    # Find tour data
    $tour = $toursJson | Where-Object { $_.id -eq $tid }
    if (-not $tour) {
        Write-Host "SKIP: $tid not in tours.json"
        continue
    }
    
    $priceFormatted = [string]::Format("{0:N0}", $tour.price)
    $nameEscaped = $tour.name -replace "'", "\'"
    
    $button = $buttonTemplate -replace '\{id\}', $tid `
                               -replace '\{name\}', $nameEscaped `
                               -replace '\{price\}', $priceFormatted `
                               -replace '\{priceNum\}', $tour.price
    
    # Insert button before <footer> tag
    if ($content -match '<footer>') {
        $content = $content -replace '<footer>', ($button + "`n<footer>")
    } else {
        Write-Host "WARN: $tid.html no <footer> tag found, inserting before </body>"
        $content = $content -replace '</body>', ($button + "`n</body>")
    }
    
    # Add cart.js script before </body> if not already there
    if ($content -notmatch 'scripts/cart\.js') {
        $content = $content -replace '</body>', ($scriptTag + "`n</body>")
    }
    
    Set-Content -Path $filePath -Value $content -Encoding UTF8
    $counter++
    Write-Host "DONE: $tid.html - $($tour.name)"
}

Write-Host "`nTotal: $counter files updated"
