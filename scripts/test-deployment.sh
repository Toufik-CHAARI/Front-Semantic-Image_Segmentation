#!/bin/bash

# Test deployment script for Streamlit Segmentation App
# Tests the application endpoint to ensure it's running correctly

set -e

# Configuration
PUBLIC_IP=${1:-"13.39.205.165"}
PORT=8501
MAX_RETRIES=5
RETRY_DELAY=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Test application endpoint
test_endpoint() {
    local url="http://$PUBLIC_IP:$PORT"
    print_status "Testing application endpoint: $url"
    
    for i in $(seq 1 $MAX_RETRIES); do
        print_status "Attempt $i of $MAX_RETRIES..."
        
        if curl -f -s "$url" > /dev/null 2>&1; then
            print_success "✅ Application is responding!"
            print_success "🌐 Streamlit app is accessible at: $url"
            return 0
        else
            print_warning "❌ Attempt $i failed"
            if [ $i -lt $MAX_RETRIES ]; then
                print_status "Waiting $RETRY_DELAY seconds before retry..."
                sleep $RETRY_DELAY
            fi
        fi
    done
    
    print_error "❌ Application is not responding after $MAX_RETRIES attempts"
    return 1
}

# Test specific endpoints
test_health_endpoints() {
    local base_url="http://$PUBLIC_IP:$PORT"
    
    print_status "Testing specific endpoints..."
    
    # Test main page
    if curl -f -s "$base_url" > /dev/null 2>&1; then
        print_success "✅ Main page is accessible"
    else
        print_warning "⚠️ Main page is not accessible"
    fi
    
    # Test with curl verbose to see response
    print_status "Getting detailed response from application..."
    curl -v "$base_url" 2>&1 | head -20
}

# Check if curl is available
if ! command -v curl &> /dev/null; then
    print_error "curl is not installed. Please install it first."
    exit 1
fi

# Main test function
main() {
    print_status "Starting deployment test for IP: $PUBLIC_IP"
    
    # Test basic connectivity
    if test_endpoint; then
        test_health_endpoints
        print_success "🎉 Deployment test completed successfully!"
        print_success "Your Streamlit segmentation app is live at: http://$PUBLIC_IP:$PORT"
    else
        print_error "💥 Deployment test failed!"
        print_status "Please check:"
        print_status "1. EC2 instance is running"
        print_status "2. Security group allows inbound traffic on port $PORT"
        print_status "3. Docker container is running on the instance"
        print_status "4. Application is properly configured"
        exit 1
    fi
}

# Show usage
usage() {
    echo "Usage: $0 [IP_ADDRESS]"
    echo ""
    echo "Arguments:"
    echo "  IP_ADDRESS    Public IP address of the EC2 instance (default: 13.36.249.197)"
    echo ""
    echo "Example:"
    echo "  $0 13.36.249.197"
    echo "  $0"
}

# Parse command line arguments
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
    exit 0
fi

# Run main test
main
