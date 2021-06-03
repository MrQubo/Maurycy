#!/usr/bin/env bash

set -o errexit -o pipefail -o nounset -o errtrace -o functrace -o noclobber
declare -r SOURCE_DIR="$(cd -- $(dirname -- "$BASH_SOURCE") && pwd)"


cd -- "$SOURCE_DIR"

if [[ ! -e discord.env ]]; then
	echo >&2 "Create discord.env file with DISCORD_TOKEN."
	exit 1
fi

if [[ ! -d venv ]]; then
	echo >&2 "Create venv with requirements.txt installed."
	exit 1
fi

. discord.env
. venv/bin/activate
clear && { tmux clear-history || true; }
exec python3 bot.py
