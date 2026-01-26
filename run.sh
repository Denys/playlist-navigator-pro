#!/bin/bash
# Playlist Navigator Pro - Easy Setup and Usage Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if Python 3 is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    print_status "Python 3 found: $(python3 --version)"
}

# Install dependencies
install_deps() {
    print_status "Installing Python dependencies..."
    if pip3 install -r requirements.txt; then
        print_status "Dependencies installed successfully"
    else
        print_warning "Failed to install some dependencies, but continuing..."
    fi
}

# Interactive playlist creation
create_playlist() {
    print_header "=== Interactive Playlist Creation ==="
    
    read -p "Enter playlist name: " playlist_name
    if [ -z "$playlist_name" ]; then
        print_error "Playlist name cannot be empty"
        exit 1
    fi
    
    # Sanitize filename
    safe_name=$(echo "$playlist_name" | tr ' ' '_' | tr -cd '[:alnum:]_-')
    output_file="${safe_name}_data.json"
    
    print_status "Creating playlist data file: $output_file"
    
    if python3 extract_playlist_data.py --interactive --output "$output_file"; then
        print_status "Playlist data created successfully"
        
        # Ask for color scheme
        echo ""
        print_header "Choose a color scheme:"
        echo "1) Purple (general tech content)"
        echo "2) Teal (audio/hardware content)"
        echo "3) Blue (programming content)"
        echo "4) Green (educational content)"
        read -p "Enter choice (1-4) [default: 1]: " color_choice
        
        case $color_choice in
            2) color_scheme="teal" ;;
            3) color_scheme="blue" ;;
            4) color_scheme="green" ;;
            *) color_scheme="purple" ;;
        esac
        
        print_status "Using color scheme: $color_scheme"
        
        # Generate the index
        print_status "Generating playlist index..."
        if python3 playlist_indexer.py --playlist-name "$playlist_name" --input-file "$output_file" --color-scheme "$color_scheme"; then
            print_status "Playlist index generated successfully!"
            
            # Show output location
            safe_playlist_name=$(echo "$playlist_name" | tr ' ' '_' | tr '[:upper:]' '[:lower:]' | tr -cd '[:alnum:]_-')
            output_dir="output/$safe_playlist_name"
            
            echo ""
            print_header "Generated files:"
            if [ -d "$output_dir" ]; then
                ls -la "$output_dir"
                echo ""
                print_status "Open $output_dir/${safe_playlist_name}_index.html in your browser to view the interactive version"
            fi
        else
            print_error "Failed to generate playlist index"
            exit 1
        fi
    else
        print_error "Failed to create playlist data"
        exit 1
    fi
}

# Process existing file
process_file() {
    print_header "=== Process Existing Playlist File ==="
    
    read -p "Enter path to JSON file: " json_file
    if [ ! -f "$json_file" ]; then
        print_error "File not found: $json_file"
        exit 1
    fi
    
    read -p "Enter playlist name: " playlist_name
    if [ -z "$playlist_name" ]; then
        print_error "Playlist name cannot be empty"
        exit 1
    fi
    
    # Ask for color scheme
    echo ""
    print_header "Choose a color scheme:"
    echo "1) Purple (general tech content)"
    echo "2) Teal (audio/hardware content)"
    echo "3) Blue (programming content)"
    echo "4) Green (educational content)"
    read -p "Enter choice (1-4) [default: 1]: " color_choice
    
    case $color_choice in
        2) color_scheme="teal" ;;
        3) color_scheme="blue" ;;
        4) color_scheme="green" ;;
        *) color_scheme="purple" ;;
    esac
    
    print_status "Processing file: $json_file"
    print_status "Using color scheme: $color_scheme"
    
    if python3 playlist_indexer.py --playlist-name "$playlist_name" --input-file "$json_file" --color-scheme "$color_scheme"; then
        print_status "Playlist index generated successfully!"
    else
        print_error "Failed to generate playlist index"
        exit 1
    fi
}

# Run example
run_example() {
    print_header "=== Running Example ==="
    print_status "This will create example playlist indexes to demonstrate the tool"
    
    if python3 example_usage.py; then
        print_status "Example completed successfully!"
        print_status "Check the 'output/' and 'example_output/' directories for results"
    else
        print_error "Example failed"
        exit 1
    fi
}

# Show help
show_help() {
    print_header "Playlist Navigator Pro - Help"
    echo ""
    echo "This script helps you create interactive indexes for YouTube playlists."
    echo ""
    echo "Options:"
    echo "  1) Create new playlist - Interactive playlist creation"
    echo "  2) Process existing file - Process an existing JSON file"
    echo "  3) Run example - See the tool in action with sample data"
    echo "  4) Install dependencies - Install required Python packages"
    echo "  5) Help - Show this help message"
    echo "  6) Exit"
    echo ""
    echo "File formats:"
    echo "  - Input: JSON file with video data"
    echo "  - Output: Markdown, HTML, and PDF files"
    echo ""
    echo "For more information, see README.md"
}

# Main menu
main_menu() {
    while true; do
        echo ""
        print_header "=== YouTube Playlist Indexer ==="
        echo "1) Create new playlist"
        echo "2) Process existing file"
        echo "3) Run example"
        echo "4) Install dependencies"
        echo "5) Help"
        echo "6) Exit"
        echo ""
        read -p "Choose an option (1-6): " choice
        
        case $choice in
            1) create_playlist ;;
            2) process_file ;;
            3) run_example ;;
            4) install_deps ;;
            5) show_help ;;
            6) 
                print_status "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid choice. Please enter 1-6."
                ;;
        esac
    done
}

# Main execution
main() {
    print_header "YouTube Playlist Indexer Setup"
    
    # Check prerequisites
    check_python
    
    # Create output directory if it doesn't exist
    mkdir -p output
    
    # If arguments provided, run directly
    if [ $# -gt 0 ]; then
        case $1 in
            "install") install_deps ;;
            "example") run_example ;;
            "help") show_help ;;
            *) 
                print_error "Unknown command: $1"
                show_help
                exit 1
                ;;
        esac
    else
        # Interactive mode
        main_menu
    fi
}

# Run main function
main "$@"

