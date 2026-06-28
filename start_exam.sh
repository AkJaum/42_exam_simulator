#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QUESTIONS_DIR="$ROOT_DIR/questions"

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 nao encontrado. Instale Python 3 para usar o simulador."
    exit 1
fi

if [ ! -d "$QUESTIONS_DIR" ]; then
    echo "Diretorio questions/ nao encontrado em: $ROOT_DIR"
    exit 1
fi

EXAMS=()
while IFS= read -r EXAM_DIR; do
    if compgen -G "$EXAM_DIR"/*/meta.json >/dev/null; then
        EXAMS+=("$(basename "$EXAM_DIR")")
    fi
done < <(find "$QUESTIONS_DIR" -mindepth 1 -maxdepth 1 -type d | sort)

if [ "${#EXAMS[@]}" -eq 0 ]; then
    echo "Nenhum exame encontrado dentro de questions/."
    exit 1
fi

echo "===================================="
echo "  42 Exam Simulator"
echo "===================================="
echo

read -r -p "Login do aluno: " LOGIN
LOGIN="${LOGIN//[^a-zA-Z0-9._-]/_}"

if [ -z "$LOGIN" ]; then
    echo "Login invalido."
    exit 1
fi

echo
echo "Exames disponiveis:"
for i in "${!EXAMS[@]}"; do
    printf "  %d - %s\n" "$((i + 1))" "${EXAMS[$i]}"
done

read -r -p "Qual exame deseja simular? " EXAM_CHOICE
if ! [[ "$EXAM_CHOICE" =~ ^[0-9]+$ ]] || [ "$EXAM_CHOICE" -lt 1 ] || [ "$EXAM_CHOICE" -gt "${#EXAMS[@]}" ]; then
    echo "Opcao de exame invalida."
    exit 1
fi

EXAM="${EXAMS[$((EXAM_CHOICE - 1))]}"

echo
echo "Modalidades:"
echo "  1 - Simulador real do exame"
echo "  2 - Simulador mata-mata"
read -r -p "Qual modalidade deseja usar? " MODE_CHOICE

case "$MODE_CHOICE" in
    1) MODE="real" ;;
    2) MODE="knockout" ;;
    *)
        echo "Opcao de modalidade invalida."
        exit 1
        ;;
esac

echo
cd "$ROOT_DIR"
python3 -m simulator.main \
    --root "$ROOT_DIR" \
    --login "$LOGIN" \
    --exam "$EXAM" \
    --mode "$MODE"
