# EC2 Connection Test Script
Write-Host "🔍 Testing EC2 Connection..." -ForegroundColor Yellow

$instance = "ec2-3-145-0-78.us-east-2.compute.amazonaws.com"
$pemFile = "DA_Workflows.pem"

Write-Host "Testing ping to $instance..." -ForegroundColor Cyan
ping $instance

Write-Host "`nTesting SSH connection..." -ForegroundColor Cyan
ssh -i $pemFile -o ConnectTimeout=10 -o StrictHostKeyChecking=no ubuntu@$instance "echo 'Connection successful!'"

Write-Host "`nTesting port 22..." -ForegroundColor Cyan
Test-NetConnection -ComputerName $instance -Port 22

Write-Host "`nConnection test complete!" -ForegroundColor Green 