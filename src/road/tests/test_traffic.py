from road.common import Direction, RoadNodeType
from road.grid import RoadSegmentNode
from road.traffic import Intersection, Vehicle
from test_helpers import config


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
    mocked_config = config.mock_config(
        grid_width=5,
        grid_height=5,
        tile_width=4,
        tile_height=4,
        road_width=2,
        vehicle_stop_wait_time=2,
        intersection_clear_time=1,
    )

    dummy_node = RoadSegmentNode(
        (0, 0), Direction.UP, RoadNodeType.ENTER, config=mocked_config
    )

    vehicles = [Vehicle(mocked_config, id, dummy_node) for id in range(10)]

    ##################
    # Basic Rotation #
    ##################

    intersct = Intersection(mocked_config)

    intersct.enqueue(vehicles[0], Direction.UP)
    intersct.enqueue(vehicles[1], Direction.RIGHT)
    intersct.enqueue(vehicles[2], Direction.DOWN)
    intersct.enqueue(vehicles[3], Direction.LEFT)
    intersct.enqueue(vehicles[4], Direction.UP)

    # Step start
    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 2, 1, 1, 1)

    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 2, 1, 1, 1)

    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 2, 1, 1, 1)

    # Elapsed: vehicle_stop_wait_time
    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 1, 1, 1, 1)
    assert intersct._last_dequeue_dir == Direction.UP
    assert intersct._clear_timer == mocked_config.INTERSECTION_CLEAR_TIME

    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 1, 1, 1, 1)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 1, 0, 1, 1)

    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 1, 0, 1, 1)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 1, 0, 0, 1)

    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 1, 0, 0, 1)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 1, 0, 0, 0)

    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 1, 0, 0, 0)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 0, 0, 0, 0)

    _assert_intersct_wait_timers(intersct, 0, 0, 0, 0)
    assert intersct._last_dequeue_dir == Direction.UP
    assert intersct._clear_timer == 1

    ####################
    # Complex Rotation #
    ####################

    intersct = Intersection(mocked_config)

    intersct.enqueue(vehicles[0], Direction.DOWN)

    # Step start
    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 0, 0, 1, 0)

    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 0, 0, 1, 0)

    intersct.enqueue(vehicles[1], Direction.LEFT)

    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 0, 0, 1, 1)

    intersct.enqueue(vehicles[2], Direction.UP)
    intersct.enqueue(vehicles[3], Direction.RIGHT)

    # Elapsed: vehicle_stop_wait_time
    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 1, 1, 0, 1)

    intersct.enqueue(vehicles[4], Direction.UP)

    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 2, 1, 0, 1)

    intersct.enqueue(vehicles[5], Direction.DOWN)
    intersct.enqueue(vehicles[6], Direction.LEFT)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 2, 1, 1, 1)

    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 2, 1, 1, 1)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 1, 1, 1, 1)

    intersct.enqueue(vehicles[7], Direction.DOWN)

    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 1, 1, 2, 1)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 1, 0, 2, 1)

    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 1, 0, 2, 1)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 1, 0, 1, 1)

    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 1, 0, 1, 1)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 1, 0, 1, 0)

    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 1, 0, 1, 0)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 0, 0, 1, 0)

    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 0, 0, 1, 0)

    # Elapsed: intersection_clear_time
    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 0, 0, 0, 0)

    intersct.step(0.5, vehicles)
    _assert_intersct_queue_lengths(intersct, 0, 0, 0, 0)
