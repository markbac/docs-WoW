#!/usr/bin/env bash
set -euo pipefail

mkdir -p tools
cd tools

# Download latest PlantUML jar (stable link maintained by PlantUML)
# If you need a fixed version, replace with a specific URL from https://github.com/plantuml/plantuml/releases
echo "Downloading PlantUML jar..."
curl -L -o plantuml.jar https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar

echo "PlantUML jar saved to tools/plantuml.jar"
