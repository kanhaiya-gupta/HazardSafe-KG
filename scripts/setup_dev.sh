#!/bin/bash

# HazardSafe-KG Development Setup Script

set -e

echo "🚀 Setting up HazardSafe-KG development environment..."

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

# Check if Python 3.11+ is installed
check_python() {
    print_status "Checking Python version..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
            print_success "Python $PYTHON_VERSION found"
        else
            print_error "Python 3.11+ is required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 is not installed"
        exit 1
    fi
}

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if command -v docker &> /dev/null; then
        print_success "Docker found"
    else
        print_warning "Docker not found. You'll need to install Docker for full functionality."
    fi
}

# Create virtual environment
setup_venv() {
    print_status "Setting up Python virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Dependencies installed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    directories=(
        "data/ontology/classes"
        "data/ontology/properties"
        "data/ontology/relationships"
        "data/ontology/constraints"
        "data/ontology/exports"
        "data/kg/neo4j"
        "data/kg/imports"
        "data/kg/exports"
        "data/kg/queries"
        "data/kg/schemas"
        "data/rag/documents/safety_data_sheets"
        "data/rag/documents/technical_specs"
        "data/rag/documents/test_protocols"
        "data/rag/documents/regulatory_docs"
        "data/rag/documents/risk_assessments"
        "data/rag/processed/chunks"
        "data/rag/processed/metadata"
        "data/rag/processed/embeddings"
        "data/rag/vector_db"
        "data/rag/models/embeddings"
        "data/rag/models/llm"
        "data/rag/models/fine_tuned"
        "data/rag/cache/embeddings_cache"
        "data/rag/cache/query_cache"
        "data/rag/cache/model_cache"
        "data/rag/exports"
        "logs"
        "uploads"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
    done
    
    print_success "Directories created"
}

# Create .env file
create_env_file() {
    print_status "Creating .env file..."
    
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# HazardSafe-KG Configuration

# Application settings
APP_NAME=HazardSafe-KG
APP_VERSION=1.0.0
DEBUG=true
SECRET_KEY=your-secret-key-change-in-production

# Database settings
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j

# Vector database settings
VECTOR_DB_TYPE=local
PINECONE_API_KEY=
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=hazardsafe-kg
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=

# LLM settings
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
DEFAULT_LLM_PROVIDER=openai
DEFAULT_EMBEDDING_MODEL=text-embedding-ada-002
DEFAULT_LLM_MODEL=gpt-3.5-turbo

# File storage settings
UPLOAD_DIR=data/rag/documents
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=[".pdf", ".docx", ".txt", ".csv"]

# Security settings
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Logging settings
LOG_LEVEL=INFO
LOG_FILE=logs/hazardsafe-kg.log

# Cache settings
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600

# API rate limiting
RATE_LIMIT_PER_MINUTE=60
EOF
        print_success ".env file created"
    else
        print_status ".env file already exists"
    fi
}

# Start Docker services
start_docker_services() {
    print_status "Starting Docker services..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d neo4j redis
        print_success "Docker services started"
        
        # Wait for services to be ready
        print_status "Waiting for services to be ready..."
        sleep 30
        
        # Check service health
        if curl -f http://localhost:7474/browser/ > /dev/null 2>&1; then
            print_success "Neo4j is ready"
        else
            print_warning "Neo4j may not be ready yet"
        fi
        
        if docker exec hazardsafe-redis redis-cli ping > /dev/null 2>&1; then
            print_success "Redis is ready"
        else
            print_warning "Redis may not be ready yet"
        fi
    else
        print_warning "docker-compose not found. Please start services manually."
    fi
}

# Initialize sample data
initialize_sample_data() {
    print_status "Initializing sample data..."
    
    # Create sample ontology data
    if [ ! -f "data/ontology/classes/hazardous_substances.ttl" ]; then
        print_status "Sample ontology data already exists"
    fi
    
    # Create sample KG data
    if [ ! -f "data/kg/imports/substances.csv" ]; then
        print_status "Sample KG data already exists"
    fi
    
    print_success "Sample data initialized"
}

# Run initial setup
run_initial_setup() {
    print_status "Running initial application setup..."
    
    # This would typically run database migrations and initial data loading
    # For now, we'll just create a simple setup script
    cat > scripts/init_app.py << 'EOF'
#!/usr/bin/env python3
"""
Initial application setup script.
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webapp.core.database import init_database
from webapp.core.vector_store import init_vector_store
from webapp.core.ontology_manager import init_ontology_manager

async def main():
    print("Initializing HazardSafe-KG application...")
    
    try:
        # Initialize database
        print("Initializing database...")
        await init_database()
        
        # Initialize vector store
        print("Initializing vector store...")
        await init_vector_store()
        
        # Initialize ontology manager
        print("Initializing ontology manager...")
        await init_ontology_manager()
        
        print("Application initialization completed successfully!")
        
    except Exception as e:
        print(f"Error during initialization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
EOF
    
    chmod +x scripts/init_app.py
    
    # Run the initialization script
    python scripts/init_app.py
    
    print_success "Application setup completed"
}

# Main setup function
main() {
    print_status "Starting HazardSafe-KG development setup..."
    
    check_python
    check_docker
    setup_venv
    install_dependencies
    create_directories
    create_env_file
    start_docker_services
    initialize_sample_data
    run_initial_setup
    
    print_success "🎉 HazardSafe-KG development environment setup completed!"
    echo
    echo "Next steps:"
    echo "1. Activate the virtual environment: source venv/bin/activate"
    echo "2. Start the application: python main.py"
    echo "3. Open your browser to: http://localhost:8000"
    echo "4. Access Neo4j browser at: http://localhost:7474"
    echo
    echo "For Docker setup:"
    echo "1. Start all services: docker-compose up -d"
    echo "2. View logs: docker-compose logs -f"
    echo "3. Stop services: docker-compose down"
    echo
    echo "Happy coding! 🚀"
}

# Run main function
main "$@" 