#!/bin/bash
# ============================================================
# Migra dados de sessoes do OpenCode entre volumes Docker
# 
# Uso: bash scripts/migrar-volumes.sh
# 
# Motivo: O nome do projeto Docker Compose mudou de
# "infraestrutura" para "authopencode-authlogin-ippaei",
# criando novos volumes vazios sem o histórico dos usuarios.
# ============================================================
set -e

OLD_PREFIX="infraestrutura"
NEW_PREFIX="authopencode-authlogin-ippaei"

USERS=("marcos" "fhelipe" "csm2" "csm3")
# Nota: csm1, lucasnunes e paolo nao tinham volume no projeto antigo

echo "=============================================="
echo " Migracao de volumes OpenCode"
echo " De: ${OLD_PREFIX}"
echo " Para: ${NEW_PREFIX}"
echo "=============================================="
echo ""

for USER in "${USERS[@]}"; do
  OLD_VOL="${OLD_PREFIX}_opencode-data-${USER}"
  NEW_VOL="${NEW_PREFIX}_opencode-data-${USER}"
  
  echo "--- Usuario: ${USER} ---"
  
  # Verifica se o volume velho existe
  if ! docker volume inspect "${OLD_VOL}" &>/dev/null; then
    echo "  ⏭️  Volume antigo ${OLD_VOL} nao existe — pulando"
    echo ""
    continue
  fi
  
  # Verifica se o volume novo existe
  if ! docker volume inspect "${NEW_VOL}" &>/dev/null; then
    echo "  ⏭️  Volume novo ${NEW_VOL} nao existe — pulando"
    echo ""
    continue
  fi
  
  echo "  Old: ${OLD_VOL}"
  echo "  New: ${NEW_VOL}"
  
  # Mostra o tamanho do volume velho
  OLD_SIZE=$(docker run --rm -v "${OLD_VOL}":/data alpine du -sh /data/ 2>/dev/null | cut -f1)
  echo "  Tamanho old: ${OLD_SIZE:-0}"
  
  # Copia dados do volume velho pro novo
  echo "  Copiando..."
  docker run --rm \
    -v "${OLD_VOL}":/old \
    -v "${NEW_VOL}":/new \
    alpine sh -c "
      cp -r /old/* /new/ 2>/dev/null
      echo '  Conteudo copiado:'
      ls -la /new/
    "
  
  # Verifica resultado
  NEW_SIZE=$(docker run --rm -v "${NEW_VOL}":/data alpine du -sh /data/ 2>/dev/null | cut -f1)
  echo "  Tamanho new apos copia: ${NEW_SIZE:-0}"
  echo ""
done

echo "=============================================="
echo " Migracao concluida!"
echo ""
echo " Proximos passos:"
echo " 1. Faca deploy do branch infra-unify no Dokploy"
echo " 2. Acesse https://ia.fvmarketing.com.br e faca login"
echo " 3. Verifique se as sessoes e modelos aparecem"
echo "=============================================="
