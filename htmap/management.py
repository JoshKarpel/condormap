from typing import Tuple, Iterator

from pathlib import Path
import shutil

from . import mapping, result, settings, utils, exceptions


def recover(map_id: str) -> result.MapResult:
    """
    Reconstruct a :class:`MapResult` from its ``map_id``.

    Parameters
    ----------
    map_id
        The ``map_id`` to search for.

    Returns
    -------
    result
        The result with the given ``map_id``.
    """
    return result.MapResult.recover(map_id)


def _map_paths() -> Iterator[Path]:
    """Yield the paths to all existing map directories."""
    try:
        yield from (settings['HTMAP_DIR'] / settings['MAPS_DIR_NAME']).iterdir()
    except FileNotFoundError:  # maps dir doesn't exist for some reason, which means we have no maps
        yield from ()


def map_ids() -> Tuple[str]:
    """Return a tuple containing the ``map_id`` for all existing maps."""
    return tuple(path.stem for path in _map_paths())


def map_results() -> Tuple[result.MapResult, ...]:
    """Return a :class:`tuple` containing the :class:`MapResult` for all existing maps."""
    return tuple(recover(map_id) for map_id in map_ids())


def remove(map_id: str, not_exist_ok = True):
    """
    Remove the map with the given ``map_id``.

    Parameters
    ----------
    map_id
        The ``map_id`` to search for and remove.
    not_exist_ok
        If ``False``, raise :class:`htmap.exceptions.MapIdNotFound` if the ``map_id`` doesn't exist.
    """
    try:
        r = recover(map_id)
        r.remove()
    except exceptions.MapIdNotFound as e:
        if not not_exist_ok:
            raise e


def force_remove(map_id: str):
    """
    Force-remove a map by trying to delete its map directory directly.

    .. warning::

        This operation is **not safe**, but might be necessary if your map directory has somehow become corrupted.

    Parameters
    ----------
    map_id
        The ``map_id`` to force-remove.
    """
    shutil.rmtree(mapping.map_dir_path(map_id), ignore_errors = True)


def clean():
    """Remove all existing maps."""
    for map_result in map_results():
        map_result.remove()


def force_clean():
    """
    Force-remove all existing maps by trying to delete their map directories directly.

    .. warning::

        This operation is **not safe**, but might be necessary if your map directory has somehow become corrupted.
    """
    for map_dir in _map_paths():
        shutil.rmtree(map_dir)


def status() -> str:
    """Return a string containing a table showing the status of all existing maps, as well as their disk usage."""
    ids = map_ids()
    results = map_results()
    counts = [r._status_counts() for r in results]

    return utils.table(
        headers = ['Map ID'] + [str(d) for d in result.JobStatus.display_statuses()] + ['Data'],
        rows = [
            [map_id] + [count[d] for d in result.JobStatus.display_statuses()] + [utils.get_dir_size_as_str(mapping.map_dir_path(map_id))]
            for map_id, count in sorted(
                zip(ids, counts),
                key = lambda map_id_and_count: map_id_and_count[1][result.JobStatus.RUNNING],
            )
        ],
    )
