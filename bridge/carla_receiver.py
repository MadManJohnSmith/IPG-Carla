"""
carla_receiver.py — Receptor event-driven para el puente IPG → CARLA.

Uso:
  Con CARLA:    python carla_receiver.py
  Sin CARLA:    python carla_receiver.py --test
"""
import argparse, math, signal, socket, struct, sys, time
import protocol

CARLA_HOST = "localhost"
CARLA_PORT = 2000
UDP_PORT = 9000
DT = 0.01
UDP_TIMEOUT = 0.5
ALPHA_PEDAL = 0.85

# Flag global para shutdown limpio
_shutdown = False
def _sig_handler(sig, frame):
    global _shutdown
    _shutdown = True
signal.signal(signal.SIGINT, _sig_handler)
signal.signal(signal.SIGTERM, _sig_handler)


class EMAFilter:
    """Filtro paso bajo con alpha compensado por dt real."""
    def __init__(self, alpha_ref, initial=0.0):
        self.alpha_ref = alpha_ref
        self.dt_ref = 0.01
        self.value = initial
    def update(self, raw, dt=0.01):
        ratio = dt / self.dt_ref if self.dt_ref > 0 else 1.0
        alpha_eff = 1.0 - math.pow(1.0 - self.alpha_ref, ratio)
        self.value += alpha_eff * (raw - self.value)
        return self.value


class _MockControl:
    def __init__(self):
        self.steer = self.throttle = self.brake = 0.0

class _MockVehicle:
    def __init__(self): self._c = _MockControl()
    def apply_control(self, c): self._c = c
    def get_control(self): return self._c

class _MockWorld:
    def __init__(self): self.tick_count = 0
    def tick(self): self.tick_count += 1


class Stats:
    def __init__(self):
        self.ticks = self.pkts_recv = self.pkts_drained = 0
        self.pkts_obsolete = self.timeouts = 0
        self.max_drain = 0
        self.max_dt = 0.0
        self.min_dt = float("inf")
        self.t0 = time.monotonic()

    def report(self):
        el = time.monotonic() - self.t0
        hz = self.ticks / el if el > 0 else 0
        print("\n" + "=" * 60)
        print("ESTADÍSTICAS DEL RECEPTOR")
        print("=" * 60)
        print(f"  Tiempo:                 {el:.2f}s")
        print(f"  Ticks:                  {self.ticks}")
        print(f"  Hz real:                {hz:.1f}")
        print(f"  Paquetes recibidos:     {self.pkts_recv}")
        print(f"  Paquetes drenados:      {self.pkts_drained}")
        print(f"  Paquetes obsoletos:     {self.pkts_obsolete}")
        print(f"  Timeouts:               {self.timeouts}")
        print(f"  Max drenado de golpe:   {self.max_drain}")
        if self.min_dt < float("inf"):
            print(f"  dt min/max:             {self.min_dt*1000:.1f}ms / {self.max_dt*1000:.1f}ms")
        print("=" * 60)


def run(vehicle, world, test_mode=False):
    global _shutdown
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", UDP_PORT))
    sock.settimeout(UDP_TIMEOUT)

    last_seq = 0
    steer_val = 0.0
    f_gas = EMAFilter(ALPHA_PEDAL)
    f_brake = EMAFilter(ALPHA_PEDAL)
    last_time = time.monotonic()
    st = Stats()

    try:
        while not _shutdown:
            # 1. Bloquear hasta paquete (event-driven)
            try:
                data, _ = sock.recvfrom(1024)
            except socket.timeout:
                st.timeouts += 1
                f_gas.update(0.0, dt=UDP_TIMEOUT)
                f_brake.update(0.5, dt=UDP_TIMEOUT)
                ctrl = _MockControl() if test_mode else __import__('carla').VehicleControl()
                ctrl.steer, ctrl.throttle, ctrl.brake = steer_val, 0.0, f_brake.value
                vehicle.apply_control(ctrl)
                world.tick()
                print("[WARN] Timeout UDP — frenado de seguridad activo")
                continue
            except OSError:
                # Socket cerrado o error de red
                break

            if _shutdown:
                break

            # 2. Drenar buffer — usar el más fresco
            drained = 0
            sock.setblocking(False)
            while True:
                try:
                    data, _ = sock.recvfrom(1024)
                    drained += 1
                except BlockingIOError:
                    break
            sock.settimeout(UDP_TIMEOUT)
            st.pkts_recv += 1 + drained
            st.pkts_drained += drained
            st.max_drain = max(st.max_drain, drained)

            # 3. Validar secuencia
            pkt = protocol.unpack(data)
            if pkt.seq <= last_seq:
                st.pkts_obsolete += 1
                continue

            # 4. dt real
            now = time.monotonic()
            dt = now - last_time
            last_time = now
            last_seq = pkt.seq
            st.max_dt = max(st.max_dt, dt)
            if dt > 0: st.min_dt = min(st.min_dt, dt)

            # Steering sin rate limiter — salto íntegro del humano
            steer_val = pkt.steer
            f_gas.update(pkt.gas, dt=dt)
            f_brake.update(pkt.brake, dt=dt)

            # 6. Aplicar control
            ctrl = _MockControl() if test_mode else __import__('carla').VehicleControl()
            ctrl.steer = steer_val
            ctrl.throttle = f_gas.value
            ctrl.brake = f_brake.value
            vehicle.apply_control(ctrl)

            # 7. Tick
            world.tick()
            st.ticks += 1

            # 8. Log periódico
            if st.ticks % 200 == 0:
                print(f"[{st.ticks:5d}] seq={pkt.seq:6d} | "
                      f"steer={steer_val:+.3f} gas={f_gas.value:.3f} "
                      f"brk={f_brake.value:.3f} | "
                      f"dt={dt*1000:.1f}ms drain={drained}")
    finally:
        st.report()
        sock.close()


def main_test():
    print("=" * 60)
    print("MODO TEST — sin CARLA, escuchando UDP en :" + str(UDP_PORT))
    print("=" * 60)
    run(_MockVehicle(), _MockWorld(), test_mode=True)


def main_carla():
    import carla
    client = carla.Client(CARLA_HOST, CARLA_PORT)
    client.set_timeout(10.0)
    world = client.get_world()
    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = DT
    world.apply_settings(settings)
    bp = world.get_blueprint_library().filter("model3")[0]
    spawn = world.get_map().get_spawn_points()[0]
    vehicle = world.spawn_actor(bp, spawn)
    vehicle.set_autopilot(False)
    pc = vehicle.get_physics_control()
    print(f"Vehículo: {vehicle.type_id} | max_steer: {pc.wheels[0].max_steer_angle}°")
    try:
        run(vehicle, world, test_mode=False)
    finally:
        settings.synchronous_mode = False
        settings.fixed_delta_seconds = None
        world.apply_settings(settings)
        vehicle.destroy()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--test", action="store_true")
    args = p.parse_args()
    main_test() if args.test else main_carla()
