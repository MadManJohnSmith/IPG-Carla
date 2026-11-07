# Mode B — CarMaker owns dynamics, CARLA renders

Mode A (implemented) sends driver inputs CarMaker → CARLA. Mode B is the reverse
relationship: CarMaker computes vehicle dynamics and CARLA follows as a
kinematic/visual puppet, with an explicit return path and time policy. Nothing
here is implemented; this page records the design material and the open
questions so the next session does not re-derive them.

## Target behaviour

- CarMaker owns the vehicle dynamics (contact, suspension, tyres).
- CARLA renders the scene and sensors; its vehicle pose is injected from
  CarMaker, not computed by CARLA physics.
- A return path CARLA → CarMaker carries whatever the control loop needs.
- Time is explicit: both platforms advance by a fixed Δt and block until both
  have finished the current step; no asynchronous free-running.
- Positioning must be reconciled with the vendor's native CarLA Interface
  (closed; CarMaker 12+), not assumed.

## Architecture proposed in the sources

The notebook notes propose a ROS2/RSDS architecture. Treat the performance
claims below as claims from those sources, not verified results.

- **Extraction:** a native C++ client built against CarMaker's C interface
  (`Vehicle.h`, `Car.h`), reading UAQs and the Raw Sensor Data Stream (RSDS)
  without perturbing the simulation core.
- **Middleware:** ROS2 (Foxy/Humble in the notes) as a deterministic
  bidirectional bridge, publishing `Car.v`, `Car.tx` and sensor data as
  `geometry_msgs/PoseStamped`, `sensor_msgs/PointCloud2`, `sensor_msgs/Image`.
- **Clock:** `use_sim_time = True`; ROS2 is the master clock and dictates the
  fixed Δt. Both platforms block until the current step completes.
- **Spatial alignment:** a static tf tree from each sensor frame to the vehicle
  CoG, then to the CARLA/Unreal global frame (X-forward, Y-right, Z-up).
- **PoC:** stream pure position from CarMaker to a CARLA ghost, then add
  orientation and sensors.

Proposals in the notes, in order of scope:

1. Synchronous digital-twin core (dynamics from CarMaker, CARLA as visual
   placeholder). Claims a 42% reduction in the dynamics Sim-to-Real gap.
2. Sensor fusion and photorealistic perception (RSI cameras/LiDAR/radar into
   ROS topics). Claims up to 82% reduction in sensor discrepancies.
3. HIL and scenario standardisation (ASAM OpenDRIVE/OpenSCENARIO, CAN-to-USB,
   `ros_canopen`, LQR/MPC with CasADi/MPCTools).
4. Perception/SLAM, AEB HIL, event-triggered MPC and multi-agent studies.

## Open questions

- Extend the existing UDP bridge, or adopt ROS2/RSDS as the notes propose?
- What exactly must cross the return path CARLA → CarMaker?
- How is the pose injected without fighting CARLA's own physics/registration?
- Which CarMaker version and licence will be available for the real tests?
- Where does the time policy live: ROS2 master clock or a custom tick loop?

## Sources (local, sensitive)

Full text in `~/Documents/research/ipg-carla-lab/notebooklm/`:
`plan-de-accion.md`,
`arquitectura-y-sincronizacion-espacial-en-co-simulacion-carmaker-ros2.md`,
`sincronismo-determinista-en-la-co-simulacion-de-vehiculos-autonomos.md`,
`propuestas-de-solucion-para-integracion.md`,
`sensores-en-carla-despues-de-integracion.md`.
