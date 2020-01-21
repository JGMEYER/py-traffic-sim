from road.common import Direction, RoadNodeType
from road.grid import RoadSegmentNode
from road.traffic import Intersection, Vehicle


def _assert_intersct_queue_lengths(intersct, u: int, r: int, d: int, l: int):
    queue_lengths = [
        len(intersct.queues[Direction.UP]),
        len(intersct.queues[Direction.RIGHT]),
        len(intersct.queues[Direction.DOWN]),
        len(intersct.queues[Direction.LEFT]),
    ]
    assert queue_lengths == [u, r, d, l]


def _assert_intersct_wait_timers(intersct, u: int, r: int, d: int, l: int):
    wait_timers = [
        intersct.wait_timers[Direction.UP],
        intersct.wait_timers[Direction.RIGHT],
        intersct.wait_timers[Direction.DOWN],
        intersct.wait_timers[Direction.LEFT],
    ]
    assert wait_timers == [u, r, d, l]


def test_intersection():
    vehicle_stop_wait_time = 2
    intersection_clear_time = 1

    dummy_node = RoadSegmentNode((0, 0), Direction.UP, RoadNodeType.ENTER)

    vehicles = [Vehicle(id, dummy_node) for id in range(10)]

    ##################
    # Basic Rotation #
    ##################

    intersct = Intersection()

    intersct.enqueue(vehicles[0], Direction.UP, vehicle_stop_wait_time)
    intersct.enqueue(vehicles[1], Direction.RIGHT, vehicle_stop_wait_time)
    intersct.enqueue(vehicles[2], Direction.DOWN, vehicle_stop_wait_time)
    intersct.enqueue(vehicles[3], Direction.LEFT, vehicle_stop_wait_time)
    intersct.enqueue(vehicles[4], Direction.UP, vehicle_stop_wait_time)

    # Step start
    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 2, 1, 1, 1)

    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 2, 1, 1, 1)

    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 2, 1, 1, 1)

    # Elapsed: vehicle_stop_wait_time
    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 1, 1, 1, 1)
    assert intersct._last_dequeue_dir == Direction.UP
    assert intersct._clear_timer == intersection_clear_time

    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 1, 1, 1, 1)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 1, 0, 1, 1)

    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 1, 0, 1, 1)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 1, 0, 0, 1)

    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 1, 0, 0, 1)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 1, 0, 0, 0)

    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 1, 0, 0, 0)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 0, 0, 0, 0)

    _assert_intersct_wait_timers(intersct, 0, 0, 0, 0)
    assert intersct._last_dequeue_dir == Direction.UP
    assert intersct._clear_timer == 1

    ####################
    # Complex Rotation #
    ####################

    intersct = Intersection()

    intersct.enqueue(vehicles[0], Direction.DOWN, vehicle_stop_wait_time)

    # Step start
    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 0, 0, 1, 0)

    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 0, 0, 1, 0)

    intersct.enqueue(vehicles[1], Direction.LEFT, vehicle_stop_wait_time)

    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 0, 0, 1, 1)

    intersct.enqueue(vehicles[2], Direction.UP, vehicle_stop_wait_time)
    intersct.enqueue(vehicles[3], Direction.RIGHT, vehicle_stop_wait_time)

    # Elapsed: vehicle_stop_wait_time
    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 1, 1, 0, 1)

    intersct.enqueue(vehicles[4], Direction.UP, vehicle_stop_wait_time)

    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 2, 1, 0, 1)

    intersct.enqueue(vehicles[5], Direction.DOWN, vehicle_stop_wait_time)
    intersct.enqueue(vehicles[6], Direction.LEFT, vehicle_stop_wait_time)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 2, 1, 1, 1)

    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 2, 1, 1, 1)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 1, 1, 1, 1)

    intersct.enqueue(vehicles[7], Direction.DOWN, vehicle_stop_wait_time)

    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 1, 1, 2, 1)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 1, 0, 2, 1)

    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 1, 0, 2, 1)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 1, 0, 1, 1)

    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 1, 0, 1, 1)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 1, 0, 1, 0)

    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 1, 0, 1, 0)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 0, 0, 1, 0)

    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 0, 0, 1, 0)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 0, 0, 0, 0)

    intersct.step(0.5, vehicles, vehicle_stop_wait_time,
                  intersection_clear_time)
    _assert_intersct_queue_lengths(intersct, 0, 0, 0, 0)
