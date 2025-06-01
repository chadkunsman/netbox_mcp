#!/bin/bash
# Example commands for testing the NetBox MCP server with MCPTools

# Make sure MCPTools is installed:
# brew tap f/mcptools && brew install mcp

# Set environment variables for the NetBox connection
export NETBOX_URL="https://your-netbox-instance.example.com"
export NETBOX_TOKEN="your_api_token"
export NETBOX_SSL_VERIFY="true"

# List all available tools in the MCP server
echo "Listing available tools:"
mcp tools python src/server.py

# Get detailed information about tools with pretty formatting
echo -e "\nDetailed tool information:"
mcp tools --format pretty python src/server.py

# Call get_device with a name parameter
echo -e "\nGetting a specific device:"
mcp call get_device --params '{"name":"example-device"}' python src/server.py

# Call get_devices with filter parameters
echo -e "\nFiltering devices by site:"
mcp call get_devices --params '{"filter_params":{"site":"NYC","limit":5}}' python src/server.py

# Call ask_about_devices with natural language query
echo -e "\nQuerying devices with natural language:"
mcp call ask_about_devices --params '{"query":"Show me all active firewalls at site NYC"}' python src/server.py

# Test more complex natural language queries
echo -e "\nQuerying with more specific natural language:"
mcp call ask_about_devices --params '{"query":"Tell me about device core-sw01"}' python src/server.py

# Run with server logs enabled to see detailed debug information
echo -e "\nRunning with server logs:"
mcp tools --server-logs python src/server.py

# Start interactive shell for manual testing
echo -e "\nStarting interactive shell for testing (press Ctrl+C to exit):"
mcp shell python src/server.py