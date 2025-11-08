#!/bin/bash
# SuperClaude Docker Test Script
# Easy testing of all SuperClaude functionality in Docker

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     SuperClaude Docker Test Environment               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to print section headers
print_section() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print info
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed!"
    echo "Install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

print_success "Docker is installed"

# Check if docker-compose is available
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    print_error "docker-compose is not available!"
    exit 1
fi

print_success "Docker Compose is available"

# Parse command line arguments
MODE="${1:-demo}"

print_section "Building SuperClaude Docker Image"

print_info "Building image..."
docker build -t superclaude:latest . 2>&1 | grep -E '(Step|Successfully built|Successfully tagged)'

print_success "Image built successfully"

# Check if .env exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found - creating from template"
    cp .env.example .env
    print_info "Edit .env file to add your API keys"
fi

# Create outputs directory
mkdir -p outputs

case $MODE in
    demo)
        print_section "Running Demo Tests (No API Keys Required)"

        print_info "Starting demo container..."
        docker run --rm \
            --name superclaude-demo \
            -v "$(pwd)/outputs:/app/outputs" \
            superclaude:latest \
            python3 examples/demo/demo_test.py

        print_success "Demo tests completed!"
        ;;

    docs)
        print_section "Starting Documentation RAG Service"

        if [ -z "$GEMINI_API_KEY" ] && ! grep -q "GEMINI_API_KEY=." .env 2>/dev/null; then
            print_warning "GEMINI_API_KEY not set in .env file"
            print_info "Demo mode will run, but real queries require API key"
        fi

        print_info "Starting documentation RAG container..."
        $DOCKER_COMPOSE --profile docs up -d superclaude-docs-rag

        print_success "Container started!"
        echo ""
        print_info "Index documentation:"
        echo "  docker exec -it superclaude-docs-rag python3 examples/gemini-file-search/superclaude_rag.py --index"
        echo ""
        print_info "Query documentation:"
        echo "  docker exec -it superclaude-docs-rag python3 examples/gemini-file-search/superclaude_rag.py --query \"How do I use MCP servers?\""
        echo ""
        print_info "Stop container:"
        echo "  $DOCKER_COMPOSE --profile docs down"
        ;;

    code)
        print_section "Starting Codebase Analysis RAG Service"

        if [ -z "$GEMINI_API_KEY" ] && ! grep -q "GEMINI_API_KEY=." .env 2>/dev/null; then
            print_warning "GEMINI_API_KEY not set in .env file"
            print_info "Real queries require API key"
        fi

        print_info "Starting codebase RAG container..."
        $DOCKER_COMPOSE --profile code up -d superclaude-code-rag

        print_success "Container started!"
        echo ""
        print_info "Index codebase:"
        echo "  docker exec -it superclaude-code-rag python3 examples/gemini-file-search/codebase_rag.py --index"
        echo ""
        print_info "Find functions:"
        echo "  docker exec -it superclaude-code-rag python3 examples/gemini-file-search/codebase_rag.py --find \"authentication logic\""
        echo ""
        print_info "Get overview:"
        echo "  docker exec -it superclaude-code-rag python3 examples/gemini-file-search/codebase_rag.py --overview"
        echo ""
        print_info "Stop container:"
        echo "  $DOCKER_COMPOSE --profile code down"
        ;;

    tv3)
        print_section "Starting TV3 Integration Service"

        if [ -z "$GEMINI_API_KEY" ] && ! grep -q "GEMINI_API_KEY=." .env 2>/dev/null; then
            print_error "GEMINI_API_KEY not set in .env file"
            exit 1
        fi

        if [ -z "$SUPABASE_URL" ] && ! grep -q "SUPABASE_URL=." .env 2>/dev/null; then
            print_error "SUPABASE_URL not set in .env file"
            exit 1
        fi

        print_info "Starting TV3 container..."
        $DOCKER_COMPOSE --profile tv3 up -d superclaude-tv3

        print_success "Container started!"
        echo ""
        print_info "Initialize news archive:"
        echo "  docker exec -it superclaude-tv3 python3 examples/tv3-integration/news_archive_rag.py --init"
        echo ""
        print_info "Index recent articles:"
        echo "  docker exec -it superclaude-tv3 python3 examples/tv3-integration/news_archive_rag.py --index-recent --days 7"
        echo ""
        print_info "Generate bulletin:"
        echo "  docker exec -it superclaude-tv3 python3 examples/tv3-integration/smart_bulletin_generator.py --daily --duration 5"
        echo ""
        print_info "Stop container:"
        echo "  $DOCKER_COMPOSE --profile tv3 down"
        ;;

    all)
        print_section "Starting All Services"

        print_info "Starting main SuperClaude container..."
        $DOCKER_COMPOSE up -d superclaude

        print_success "All services started!"
        echo ""
        print_info "View logs:"
        echo "  $DOCKER_COMPOSE logs -f"
        echo ""
        print_info "Run commands:"
        echo "  docker exec -it superclaude bash"
        echo ""
        print_info "Stop all:"
        echo "  $DOCKER_COMPOSE down"
        ;;

    build)
        print_section "Rebuilding Docker Image"

        print_info "Rebuilding image with no cache..."
        docker build --no-cache -t superclaude:latest .

        print_success "Image rebuilt successfully!"
        ;;

    clean)
        print_section "Cleaning Docker Environment"

        print_info "Stopping all containers..."
        $DOCKER_COMPOSE --profile demo down 2>/dev/null || true
        $DOCKER_COMPOSE --profile docs down 2>/dev/null || true
        $DOCKER_COMPOSE --profile code down 2>/dev/null || true
        $DOCKER_COMPOSE --profile tv3 down 2>/dev/null || true
        $DOCKER_COMPOSE down 2>/dev/null || true

        print_info "Removing SuperClaude images..."
        docker rmi superclaude:latest 2>/dev/null || true

        print_info "Cleaning build cache..."
        docker builder prune -f

        print_success "Docker environment cleaned!"
        ;;

    shell)
        print_section "Opening Interactive Shell"

        print_info "Starting interactive shell in SuperClaude container..."
        docker run --rm -it \
            --name superclaude-shell \
            -v "$(pwd)/.env:/app/.env:ro" \
            -v "$(pwd)/outputs:/app/outputs" \
            -v "$(pwd):/app/workspace:ro" \
            superclaude:latest \
            /bin/bash
        ;;

    help|--help|-h)
        echo "SuperClaude Docker Test Script"
        echo ""
        echo "Usage: ./docker-test.sh [mode]"
        echo ""
        echo "Modes:"
        echo "  demo    - Run demo tests (no API keys required) [default]"
        echo "  docs    - Start documentation RAG service"
        echo "  code    - Start codebase analysis RAG service"
        echo "  tv3     - Start TV3 integration service"
        echo "  all     - Start all services"
        echo "  build   - Rebuild Docker image"
        echo "  clean   - Clean Docker environment"
        echo "  shell   - Open interactive shell"
        echo "  help    - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./docker-test.sh demo          # Run demo tests"
        echo "  ./docker-test.sh docs          # Start docs RAG"
        echo "  ./docker-test.sh shell         # Interactive shell"
        echo ""
        ;;

    *)
        print_error "Unknown mode: $MODE"
        echo "Run './docker-test.sh help' for usage information"
        exit 1
        ;;
esac

echo ""
print_section "Documentation"
echo "📖 Docker Guide: DOCKER_DEPLOYMENT.md"
echo "📖 Quick Start: QUICK_START.md"
echo "📖 File Search: GEMINI_FILE_SEARCH.md"
echo "📖 TV3 Integration: TV3_INTEGRATION_PLAN.md"
echo ""
