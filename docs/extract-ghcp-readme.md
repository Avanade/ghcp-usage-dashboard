## Using the PowerShell Script
Using the PowerShell Script (Standalone) to Extract GitHub Copilot Usage Data.

The [`extract-ghcp-usage-data.ps1`](./powershell/extract-ghcp-usage-data.ps1) PowerShell script is designed to fetch and normalize GitHub Copilot usage data for your organization. This guide will walk you through the steps to use the script effectively.

#### Prerequisites

Before running the script, ensure you have the following:

1. **PowerShell**: Make sure you have PowerShell installed on a **Windows** machine.
2. **GitHub Copilot REST API Token**: You need a valid GitHub Copilot REST API token. Follow these instructions to generate a personal access token: [Managing your personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).
3. **Organization Name**: The name of your GitHub organization.
4. The following permissions set in for your GitHub organization profile:

- [x] copilot
  - [x] manage_billing:copilot


#### Setting Up Environment Variables

The script relies on environment variables to authenticate and fetch data from the GitHub API. You need to set the following environment variables:

- `GHCP_TOKEN`: Your GitHub Copilot REST API token.
- `ORG_NAME`: The name of your GitHub organization.

You can set these environment variables in your PowerShell session using the following commands:

```powershell
Set-Item -Path Env:GHCP_TOKEN -Value "your-ghcp-token"
Set-Item -Path Env:ORG_NAME -Value "your-org-name"
```

Alternatively, you can add these variables to your system environment variables.

#### Running the Script

1.  **Save the script**: Save the `extract-ghcp-usage-data.ps1` script to your local machine.

2. **Navigate to the Directory**: Open a PowerShell terminal and navigate to the directory containing the `extract-ghcp-usage-data.ps1` script.

3. **Execute the Script**: Run the script using the following command:

```powershell
.\extract-ghcp-usage-data.ps1
```

#### Script Output

The script performs the following actions:

1. **Fetches Copilot Usage Data**: Calls the GitHub API to retrieve seats and usage data for your organization.
2. **Normalizes the Data**: Processes and normalizes the data to ensure it is in a consistent format.
3. **Exports Data to CSV**: Saves the normalized data to CSV files in the `data` directory. The `data` directory is created automaticall under the `powershell` directory if it does not exist.

The script generates two CSV files:

- `ghcp-seats-data-YYYY-MM-DD.csv`
- `ghcp-usage-data-YYYY-MM-DD.csv`

The `YYYY-MM-DD` part of the file name corresponds to the date when the script was run.

#### Example Output

After running the script, you should see output similar to the following:

```plaintext
Copilot usage data saved to data/ghcp-seats-data-2024-07-11.csv
Usage data saved to data/ghcp-usage-data-2024-07-11.csv
```

#### Troubleshooting

- **Invalid Token**: Ensure your `GHCP_TOKEN` is correct and has the necessary permissions.
- **Network Issues**: Check your internet connection if the script fails to fetch data. Verify if you require any firewall or proxy settings.
- **Environment Variables**: Verify that the environment variables are set correctly.