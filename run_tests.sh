#!/bin/bash

# Script para executar testes do Contexta
# Uso: ./run_tests.sh [opções]

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Contexta Test Runner ===${NC}"
echo ""

# Verificar se Poetry está instalado
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}Poetry não está instalado. Por favor, instale Poetry primeiro.${NC}"
    exit 1
fi

# Exportar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Parse argumentos
TEST_TYPE="${1:-all}"

case $TEST_TYPE in
    "all")
        echo -e "${YELLOW}Executando todos os testes...${NC}"
        poetry run pytest -v
        ;;
    "cov")
        echo -e "${YELLOW}Executando testes com cobertura...${NC}"
        poetry run pytest --cov --cov-report=term-missing --cov-report=html
        echo -e "${GREEN}Relatório HTML gerado em: htmlcov/index.html${NC}"
        ;;
    "unit")
        echo -e "${YELLOW}Executando testes unitários...${NC}"
        poetry run pytest -m unit -v
        ;;
    "integration")
        echo -e "${YELLOW}Executando testes de integração...${NC}"
        poetry run pytest -m integration -v
        ;;
    "watch")
        echo -e "${YELLOW}Executando testes em modo watch...${NC}"
        poetry run pytest-watch
        ;;
    "fast")
        echo -e "${YELLOW}Executando testes rápidos (sem testes marcados como slow)...${NC}"
        poetry run pytest -m "not slow" -v
        ;;
    *)
        echo -e "${RED}Opção inválida: $TEST_TYPE${NC}"
        echo ""
        echo "Uso: $0 [all|cov|unit|integration|watch|fast]"
        echo ""
        echo "Opções:"
        echo "  all         - Executar todos os testes (padrão)"
        echo "  cov         - Executar testes com relatório de cobertura"
        echo "  unit        - Executar apenas testes unitários"
        echo "  integration - Executar apenas testes de integração"
        echo "  watch       - Executar testes em modo watch (reexecuta ao salvar)"
        echo "  fast        - Executar apenas testes rápidos"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✓ Testes concluídos!${NC}"

