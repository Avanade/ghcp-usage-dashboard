# Load environment variables
$env:GHCP_TOKEN = [System.Environment]::GetEnvironmentVariable("GHCP_TOKEN")
$env:ORG_NAME = [System.Environment]::GetEnvironmentVariable("ORG_NAME")

# Validate environment variables
if ([string]::IsNullOrEmpty($env:GHCP_TOKEN) -or [string]::IsNullOrEmpty($env:ORG_NAME)) {
    Write-Error "Required environment variables GHCP_TOKEN and/or ORG_NAME are not set."
    exit 1
}

# Set the headers
$headers = @{
    'Accept' = 'application/vnd.github+json'
    'Authorization' = "Bearer $env:GHCP_TOKEN"
    'X-GitHub-Api-Version' = '2022-11-28'
}

# Set the API endpoint for usage data
$usage_data_url = "https://api.github.com/orgs/$($env:ORG_NAME)/copilot/metrics"

# Function to make API calls with error handling
function Invoke-GithubAPI {
    param (
        [string]$Uri,
        [hashtable]$Headers
    )
    try {
        $response = Invoke-RestMethod -Uri $Uri -Headers $Headers -Method Get
        return $response
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        $message = $_.ErrorDetails.Message
        
        Write-Error "API call failed with status code $statusCode. Error: $message"
        if ($statusCode -eq 401) {
            Write-Error "Authentication failed. Please check your GHCP_TOKEN."
        }
        return $null
    }
}

# Function to get the response from usage
function Get-ResponseFromUsage {
    return Invoke-GithubAPI -Uri $usage_data_url -Headers $headers
}

# Function to get the Copilot usage
function Get-CopilotSeats {
    $billing_users_url = "https://api.github.com/orgs/$($env:ORG_NAME)/copilot/billing"
    $response = Invoke-GithubAPI -Uri $billing_users_url -Headers $headers
    
    if ($null -eq $response) {
        return $null
    }

    # Parse the JSON response
    $seat_breakdown = $response.seat_breakdown
    return @{
        added_this_cycle = $seat_breakdown.added_this_cycle
        active_this_cycle = $seat_breakdown.active_this_cycle
        inactive_this_cycle = $seat_breakdown.inactive_this_cycle
        total = $seat_breakdown.total
    }
}

# Function to normalize usage data
function Normalize-UsageData {
    param (
        [Parameter(Mandatory=$true)]
        [PSCustomObject]$usage_data
    )

    $normalizedData = @()
    
    # Process IDE code completions
    foreach ($editor in $usage_data.copilot_ide_code_completions.editors) {
        foreach ($model in $editor.models) {
            foreach ($language in $model.languages) {
                $normalizedItem = [PSCustomObject]@{
                    date                      = [string]$usage_data.date
                    total_active_users        = [string]$usage_data.total_active_users
                    total_engaged_users       = [string]$usage_data.total_engaged_users
                    feature_type              = "ide_code"
                    editor                    = [string]$editor.name
                    model_name               = [string]$model.name
                    is_custom_model          = [string]$model.is_custom_model
                    custom_model_training_date = [string]$model.custom_model_training_date
                    language                  = [string]$language.name
                    engaged_users            = [string]$language.total_engaged_users
                    suggestions_count        = [string]$language.total_code_suggestions
                    acceptances_count        = [string]$language.total_code_acceptances
                    lines_suggested          = [string]$language.total_code_lines_suggested
                    lines_accepted           = [string]$language.total_code_lines_accepted
                }
                $normalizedData += $normalizedItem
            }
        }
    }

    # Process IDE chat
    foreach ($editor in $usage_data.copilot_ide_chat.editors) {
        foreach ($model in $editor.models) {
            $normalizedItem = [PSCustomObject]@{
                date                      = [string]$usage_data.date
                total_active_users        = [string]$usage_data.total_active_users
                total_engaged_users       = [string]$usage_data.total_engaged_users
                feature_type              = "ide_chat"
                editor                    = [string]$editor.name
                model_name               = [string]$model.name
                is_custom_model          = [string]$model.is_custom_model
                custom_model_training_date = [string]$model.custom_model_training_date
                language                  = ""
                engaged_users            = [string]$model.total_engaged_users
                total_chats              = [string]$model.total_chats
                chat_insertions          = [string]$model.total_chat_insertion_events
                chat_copies              = [string]$model.total_chat_copy_events
            }
            $normalizedData += $normalizedItem
        }
    }

    # Process GitHub.com chat
    foreach ($model in $usage_data.copilot_dotcom_chat.models) {
        $normalizedItem = [PSCustomObject]@{
            date                      = [string]$usage_data.date
            total_active_users        = [string]$usage_data.total_active_users
            total_engaged_users       = [string]$usage_data.total_engaged_users
            feature_type              = "dotcom_chat"
            editor                    = "github.com"
            model_name               = [string]$model.name
            is_custom_model          = [string]$model.is_custom_model
            custom_model_training_date = [string]$model.custom_model_training_date
            engaged_users            = [string]$model.total_engaged_users
            total_chats              = [string]$model.total_chats
        }
        $normalizedData += $normalizedItem
    }

    # Process Pull Requests
    foreach ($repo in $usage_data.copilot_dotcom_pull_requests.repositories) {
        foreach ($model in $repo.models) {
            $normalizedItem = [PSCustomObject]@{
                date                      = [string]$usage_data.date
                total_active_users        = [string]$usage_data.total_active_users
                total_engaged_users       = [string]$usage_data.total_engaged_users
                feature_type              = "pull_requests"
                repository               = [string]$repo.name
                model_name               = [string]$model.name
                is_custom_model          = [string]$model.is_custom_model
                custom_model_training_date = [string]$model.custom_model_training_date
                engaged_users            = [string]$model.total_engaged_users
                pr_summaries_created     = [string]$model.total_pr_summaries_created
            }
            $normalizedData += $normalizedItem
        }
    }

    return $normalizedData
}

# Get the Copilot Seats data
$copilot_seats = Get-CopilotSeats

# Create the data folder if it doesn't exist
$dataFolder = Join-Path $PSScriptRoot ".." "data"
if (-not (Test-Path -Path $dataFolder)) {
    New-Item -ItemType Directory -Path $dataFolder | Out-Null
}

# Get today's date
$dateToday = Get-Date -Format "yyyy-MM-dd"

# Define the CSV file paths
$csvFilePathSeats = Join-Path $dataFolder "ghcp-seats-data-$dateToday.csv"
$csvFilePathUsage = Join-Path $dataFolder "ghcp-usage-data-$dateToday.csv"

# Save the Copilot seats data if available
if ($null -ne $copilot_seats) {
    $copilot_seats | Export-Csv -Path $csvFilePathSeats -NoTypeInformation
    Write-Output "Copilot seats data saved to $csvFilePathSeats"
} else {
    Write-Warning "No Copilot seats data available to save"
}

### Usage Data
# Get the response from usage api
$usage_data = Get-ResponseFromUsage

if ($null -ne $usage_data) {
    # Check if $usage_data is an array
    if ($usage_data -is [System.Collections.IEnumerable]) {
        $allNormalizedData = @()
        foreach ($data in $usage_data) {
            if ($null -ne $data) {
                $allNormalizedData += Normalize-UsageData -usage_data $data
            }
        }
        if ($allNormalizedData.Count -gt 0) {
            $allNormalizedData | Export-Csv -Path $csvFilePathUsage -NoTypeInformation
            Write-Output "Usage data saved to $csvFilePathUsage"
        } else {
            Write-Warning "No valid usage data to save"
        }
    } else {
        $normalizedData = Normalize-UsageData -usage_data $usage_data
        if ($null -ne $normalizedData) {
            $normalizedData | Export-Csv -Path $csvFilePathUsage -NoTypeInformation
            Write-Output "Usage data saved to $csvFilePathUsage"
        } else {
            Write-Warning "No valid usage data to save"
        }
    }
} else {
    Write-Warning "Failed to retrieve usage data"
}