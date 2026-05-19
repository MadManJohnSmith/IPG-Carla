"""
udp_stress_test.py — 7 escenarios de estrés para carla_receiver.py.

Uso: python udp_stress_test.py [--port 9000]
"""
import argparse, math, socket, time
import protocol

TARGET = ("127.0.0.1", 9000)
PERIOD = 1.0 / 100


def send(sock, seq, steer, gas, brake):
    sock.sendto(protocol.pack(seq, steer, gas, brake), TARGET)


def steady(sock, seq, steer, gas, brake, dur):
    t0 = time.perf_counter()
    nt = t0
    while time.perf_counter() - t0 < dur:
        seq += 1; send(sock, seq, steer, gas, brake)
        nt += PERIOD
        while time.perf_counter() < nt: pass
    return seq


def s1_normal(sock, seq, dur=3.0):
    print(f"\n[1] Flujo normal 100Hz — {dur}s")
    t0 = time.perf_counter(); nt = t0; n = 0
    while time.perf_counter() - t0 < dur:
        t = time.perf_counter() - t0
        seq += 1; n += 1
        send(sock, seq, 0.3*math.sin(math.pi*t), 0.4+0.1*math.sin(0.4*math.pi*t), 0.0)
        nt += PERIOD
        while time.perf_counter() < nt: pass
    print(f"  → {n} paquetes"); return seq


def s2_burst(sock, seq, size=500):
    print(f"\n[2] Ráfaga {size} paquetes instantáneos")
    for i in range(size):
        seq += 1; send(sock, seq, 0.2+0.001*i, 0.5, 0.0)
    time.sleep(0.5); print(f"  → {size} enviados"); return seq


def s3_gap(sock, seq, gap_ms=200):
    print(f"\n[3] Hueco de {gap_ms}ms")
    seq = steady(sock, seq, 0.1, 0.6, 0.0, 1.0)
    print(f"  → Pausa {gap_ms}ms..."); time.sleep(gap_ms/1000.0)
    seq = steady(sock, seq, 0.1, 0.3, 0.1, 1.0)
    print(f"  → Reanudado"); return seq


def s4_ooo(sock, seq):
    print(f"\n[4] Paquetes desordenados")
    for ds, st in [(3,.15),(1,.10),(2,.12),(5,.20),(4,.18)]:
        send(sock, seq+ds, st, 0.5, 0.0); time.sleep(0.005)
    seq += 5; time.sleep(0.5); print(f"  → 5 OOO enviados"); return seq


def s5_evasive(sock, seq):
    print(f"\n[5] Maniobra evasiva steer -0.8→+0.8")
    seq = steady(sock, seq, -0.8, 0.5, 0.0, 1.0)
    seq += 1; send(sock, seq, 0.8, 0.5, 0.0)
    seq = steady(sock, seq, 0.8, 0.5, 0.0, 2.0)
    print(f"  → Rate limiter debería suavizar"); return seq


def s6_ebrake(sock, seq):
    print(f"\n[6] Frenada de emergencia")
    seq = steady(sock, seq, 0.0, 0.9, 0.0, 1.0)
    seq = steady(sock, seq, 0.0, 0.0, 1.0, 1.5)
    print(f"  → gas 0.9→0, brake 0→1"); return seq


def s7_disconnect(sock, seq):
    print(f"\n[7] Desconexión 2s")
    time.sleep(2.0)
    seq = steady(sock, seq, 0.0, 0.3, 0.0, 1.0)
    print(f"  → Reconectado"); return seq


def main():
    global TARGET
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=9000)
    a = p.parse_args()
    TARGET = ("127.0.0.1", a.port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    seq = 0
    print("=" * 60)
    print(f"STRESS TEST → {TARGET[0]}:{TARGET[1]}")
    print("=" * 60)
    time.sleep(1)
    t0 = time.monotonic()
    seq = s1_normal(sock, seq)
    seq = s2_burst(sock, seq)
    seq = s3_gap(sock, seq)
    seq = s4_ooo(sock, seq)
    seq = s5_evasive(sock, seq)
    seq = s6_ebrake(sock, seq)
    seq = s7_disconnect(sock, seq)
    seq = s1_normal(sock, seq, 2.0)
    el = time.monotonic() - t0
    print(f"\n{'='*60}\nCOMPLETADO — {el:.1f}s, {seq} paquetes\n{'='*60}")
    sock.close()

if __name__ == "__main__":
    main()
