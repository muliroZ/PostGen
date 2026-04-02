#!/bin/bash

GREEN='\033[0;32m'
NC='\033[0m'

echo "Iniciando a instalação do PostGen CLI..."

PROJECT_DIR=$(pwd)
CLI_SCRIPT="$PROJECT_DIR/core/cli.py"

if [ ! -f "$CLI_SCRIPT" ]; then
    echo "Erro: Ficheiro $CLI_SCRIPT não encontrado."
    echo "Certifique-se de executar este script na raiz do projeto PostGen."
    exit 1
fi

chmod +x "$CLI_SCRIPT"

WRAPPER_PATH="/usr/local/bin/post-gen"

echo "Será solicitada a senha de administrador (sudo) para instalar o comando globalmente em $WRAPPER_PATH"

sudo rm /usr/local/bin/post-gen 2>/dev/null

sudo tee $WRAPPER_PATH > /dev/null <<EOF
#!/bin/bash
cd $PROJECT_DIR && uv run core/cli.py "\$@"
EOF

sudo chmod +x $WRAPPER_PATH

echo -e "${GREEN}PostGen CLI instalado com sucesso!${NC}"
echo "Você pode usar o comando 'post-gen' no seu terminal para acessar a CLI de geração de conteúdo."
