# Load environment variables
$env:GHCP = [System.Environment]::GetEnvironmentVariable("GHCP_TOKEN")
$env:ORG_NAME = [System.Environment]::GetEnvironmentVariable("ORG_NAME")

# Set the headers
$headers = @{
    'Accept' = 'application/vnd.github+json'
    'Authorization' = "Bearer $env:GHCP_TOKEN"
    'X-GitHub-Api-Version' = '2022-11-28'
}

# Set the API endpoint for usage data
$usage_data_url = "https://api.github.com/orgs/$($env:ORG_NAME)/copilot/usage"

# Function to get the response from usage
function Get-ResponseFromUsage {
    # Call the API to get the usage data
    $response = Invoke-RestMethod -Uri $usage_data_url -Headers $headers -Method Get

    # Return the response
    return $response
}

# Function to get the Copilot usage
function Get-CopilotSeats {
    # Call the API to get the number of users
    $billing_users_url = "https://api.github.com/orgs/$($env:ORG_NAME)/copilot/billing"
    $response = Invoke-RestMethod -Uri $billing_users_url -Headers $headers -Method Get

    # Parse the JSON response
    $seat_breakdown = $response.seat_breakdown
    $added_this_cycle = $seat_breakdown.added_this_cycle
    $active_this_cycle = $seat_breakdown.active_this_cycle
    $inactive_this_cycle = $seat_breakdown.inactive_this_cycle
    $total = $seat_breakdown.total

    return @{
        added_this_cycle = $added_this_cycle
        active_this_cycle = $active_this_cycle
        inactive_this_cycle = $inactive_this_cycle
        total = $total
    }
}

# Function to normalize usage data
function Normalize-UsageData {
    param (
        [Parameter(Mandatory=$true)]
        [PSCustomObject]$usage_data
    )

    $normalizedData = @()
    foreach ($item in $usage_data.breakdown) {
        $normalizedItem = [PSCustomObject]@{
            day                     = [string]$usage_data.day
            total_suggestions_count = [string]$usage_data.total_suggestions_count
            total_acceptances_count = [string]$usage_data.total_acceptances_count
            total_lines_suggested   = [string]$usage_data.total_lines_suggested
            total_lines_accepted    = [string]$usage_data.total_lines_accepted
            total_active_users      = [string]$usage_data.total_active_users
            total_chat_acceptances  = [string]$usage_data.total_chat_acceptances
            total_chat_turns        = [string]$usage_data.total_chat_turns
            total_active_chat_users = [string]$usage_data.total_active_chat_users
            language                = [string]$item.language
            editor                  = [string]$item.editor
            suggestions_count       = [string]$item.suggestions_count
            acceptances_count       = [string]$item.acceptances_count
            lines_suggested         = [string]$item.lines_suggested
            lines_accepted          = [string]$item.lines_accepted
            active_users            = [string]$item.active_users
        }
        $normalizedData += $normalizedItem
    }
    return $normalizedData
}

# Get the Copilot Seats data
$copilot_seats = Get-CopilotSeats

# Create the data folder if it doesn't exist
$dataFolder = "data"
if (-not (Test-Path -Path $dataFolder)) {
    New-Item -ItemType Directory -Path $dataFolder
}

# Get today's date
$dateToday = Get-Date -Format "yyyy-MM-dd"

# Define the CSV file path for Copilot usage
$csvFilePathSeats = "$dataFolder/ghcp-seats-data-$dateToday.csv"

# Save the Copilot usage results to the CSV file
$copilot_seats | Export-Csv -Path $csvFilePathSeats -NoTypeInformation

### Usage Data

# Get the response from usage api
$usage_data = Get-ResponseFromUsage

# Define the CSV file path for usage data
$csvFilePathUsage = "$dataFolder/ghcp-usage-data-$dateToday.csv"

# Check if $usage_data is an array
if ($usage_data -is [System.Collections.IEnumerable]) {
    $allNormalizedData = @()
    foreach ($data in $usage_data) {
        $allNormalizedData += Normalize-UsageData -usage_data $data
    }
    $allNormalizedData | Export-Csv -Path $csvFilePathUsage -NoTypeInformation
} else {
    $normalizedData = Normalize-UsageData -usage_data $usage_data
    $normalizedData | Export-Csv -Path $csvFilePathUsage -NoTypeInformation
}

Write-Output "Copilot usage data saved to $csvFilePathSeats"
Write-Output "Usage data saved to $csvFilePathUsage"