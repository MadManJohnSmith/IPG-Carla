#!/bin/bash
# run_test.sh — Lanza receptor y stress test, captura estadísticas.
set -e
cd "$(dirname "$0")"

# Cleanup
pkill -9 -f "carla_receiver.py" 2>/dev/null || true
sleep 0.3

echo "=== Lanzando receptor en modo test ==="
python3 carla_receiver.py --test &
RCVPID=$!
sleep 1.5

echo "=== Lanzando stress test ==="
python3 udp_stress_test.py
echo "=== Stress test completado ==="

# Esperar que el receptor procese los últimos paquetes
sleep 1

# Enviar SIGTERM (el signal handler lo captura y sale limpiamente)
echo "=== Deteniendo receptor (PID=$RCVPID) ==="
kill -TERM $RCVPID 2>/dev/null || true
wait $RCVPID 2>/dev/null || true

echo "=== DONE ==="
