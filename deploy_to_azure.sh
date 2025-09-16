#!/bin/bash

# Azure Deployment Script for Reddit Agent MVP
# This script automates the deployment process to Azure Web App

set -e  # Exit on any error

# Configuration
RESOURCE_GROUP="reddit-agent-rg"
APP_SERVICE_PLAN="reddit-agent-plan"
WEB_APP_NAME="reddit-agent-mvp"
LOCATION="East US"

echo "🚀 Starting Azure deployment for Reddit Agent MVP..."
echo "=================================================="

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if user is logged in
if ! az account show &> /dev/null; then
    echo "🔐 Please log in to Azure:"
    az login
fi

echo "✅ Azure CLI is ready"

# Create resource group
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location "$LOCATION" --output table

# Create App Service Plan
echo "🏗️ Creating App Service Plan..."
az appservice plan create \
    --name $APP_SERVICE_PLAN \
    --resource-group $RESOURCE_GROUP \
    --sku B1 \
    --is-linux \
    --output table

# Create Web App
echo "🌐 Creating Web App..."
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --name $WEB_APP_NAME \
    --runtime "PYTHON|3.9" \
    --deployment-local-git \
    --output table

# Configure environment variables
echo "⚙️ Configuring environment variables..."
echo "Please enter your Reddit API credentials:"

read -p "Reddit Client ID: " REDDIT_CLIENT_ID
read -p "Reddit Client Secret: " REDDIT_CLIENT_SECRET
read -p "Reddit Username: " REDDIT_USERNAME
read -s -p "Reddit Password: " REDDIT_PASSWORD
echo

# Set Reddit environment variables
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --settings \
    REDDIT_CLIENT_ID="$REDDIT_CLIENT_ID" \
    REDDIT_CLIENT_SECRET="$REDDIT_CLIENT_SECRET" \
    REDDIT_USERNAME="$REDDIT_USERNAME" \
    REDDIT_PASSWORD="$REDDIT_PASSWORD" \
    USER_AGENT="reddit-agent-mvp/1.0" \
    WEBSITES_ENABLE_APP_SERVICE_STORAGE="true" \
    WEBSITES_PORT="8000" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true"

echo "✅ Environment variables configured"

# Configure startup command
echo "🚀 Configuring startup command..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --startup-file "startup.sh"

# Get deployment URL
DEPLOYMENT_URL=$(az webapp deployment source config-local-git \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --query url --output tsv)

echo "✅ Azure resources created successfully!"
echo "=================================================="
echo "📋 Deployment Summary:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Web App Name: $WEB_APP_NAME"
echo "   App URL: https://$WEB_APP_NAME.azurewebsites.net"
echo "   Deployment URL: $DEPLOYMENT_URL"
echo ""
echo "🔧 Next Steps:"
echo "1. Add the deployment remote to your git repository:"
echo "   git remote add azure $DEPLOYMENT_URL"
echo ""
echo "2. Deploy your application:"
echo "   git push azure main"
echo ""
echo "3. Monitor your application:"
echo "   az webapp log tail --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME"
echo ""
echo "🎉 Your Reddit Agent MVP is ready for deployment!"
