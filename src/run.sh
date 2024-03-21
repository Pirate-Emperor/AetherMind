#!/bin/bash
if ! pgrep -f AetherMind.py > /dev/null
then
	cd "$(dirname "$0")"
	nohup \
	/home/$(whoami)/miniconda3/envs/aether/bin/python /home/$(whoami)/miniconda3/envs/aether/bin/streamlit run AetherMind.py	\
	--server.headless true \
	--server.address 0.0.0.0 \
	--server.port 8601 \
	--browser.gatherUsageStats false \
	> output.log 2>&1 &
fi
