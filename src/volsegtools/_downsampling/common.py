import math

from volsegtools._core import Bytes
from volsegtools._storage import Channel


def calculate_approx_downsampled_sizes(
    channel: Channel | int, threshold: int, factor: int = 2
) -> list[float]:
    """Calculates approximate downsampling sizes.

    Parameters
    ----------
    channel
        The source of the original resolution.
    size_threshold
        The minimal size for a resolution to be accepted.
    factor
        A single dimension of the downsampling kernel. So factor equal to 2
        would result into 1/8th of the size of the previous resolution.

    Raises
    ------
    RuntimeError
        If the factor is smaller than 2, because that wouldn't lead to any
        downsampling.
        If the threshold is smaller or equal to 0, because that would lead to
        infine calculation of approximations.

    Returns
    -------
    list[float]
        List of approximate downsampled sizes of different resolutions.
    """
    if factor <= 1:
        raise RuntimeError("Factor <= 1 wouldn't lead to downsampling")

    if threshold <= 0:
        raise RuntimeError("Size threshold has to be bigger than zero")

    nbytes = channel.handle.nbytes if isinstance(channel, Channel) else channel

    sizes = []
    while nbytes > threshold:
        nbytes /= factor**3
        if nbytes < threshold:
            break
        sizes.append(nbytes)
    return sizes


def calculate_dimensions(
    channel: Channel | tuple[int, ...], factor: int = 2
) -> list[tuple[int, ...]]:
    """Calculates resulting dimensions from downsampling.

    Parameters
    ----------
    channel
        The source of the original resolution.
    factor
        A single dimension of the downsampling kernel. So factor equal to 2
        would result into 1/8th of the size of the previous resolution.

    Raises
    ------
    RuntimeError
        If the factor is smaller than 2, because that wouldn't lead to any
        downsampling.

    Returns
    -------
    list[tuple[int, ...]]
        List of dimensions per resolution.
    """
    if factor <= 1:
        raise RuntimeError("Factor <= 1 wouldn't lead to downsampling")

    def is_valid(shape):
        return all(x > 0 for x in shape)

    shape = channel.handle.shape if isinstance(channel, Channel) else channel

    dimensions = []
    while True:
        shape = tuple(x // factor for x in shape)
        if is_valid(shape):
            dimensions.append(shape)
        else:
            break
    return dimensions


def calculate_threshold_for_resolution(
    channel: Channel | int, resolution_cnt: int, factor: int = 2
) -> Bytes:
    """Calculates size threshold from the desired number of resolutions.

    Parameters
    ----------
    channel
        The source of the original resolution.
    resolution_cnt
        The desired count of resolutions.
    factor
        A single dimension of the downsampling kernel. So factor equal to 2
        would result into 1/8th of the size of the previous resolution.

    Raises
    ------
    RuntimeError
        If the count of resolutions is smaller than 2, because that wouldn't
        to lead to any downsampling.
        If the factor is smaller than 2, because that wouldn't lead to any
        downsampling.

    Returns
    -------
    Bytes:
        Desired size threshold in bytes. The number might be 1! In that case
        it might not be possible to reach desired count of resolution levels.
    """
    if resolution_cnt <= 1:
        raise RuntimeError("Count of resolutions has to be bigger than 2")

    if factor <= 1:
        raise RuntimeError("Factor <= 1 wouldn't lead to downsampling")

    nbytes = channel.handle.nbytes if isinstance(channel, Channel) else channel

    min_size = nbytes
    for _ in range(resolution_cnt):
        nbytes /= factor**3
        nbytes = int(nbytes)
        if math.isclose(nbytes, 0):
            break
        min_size = nbytes
    return Bytes(min_size)


def calculate_steps(channel: Channel | int, threshold: int, factor: int = 2) -> int:
    """Calculates the number of downsampling steps.

    See: calculate_approx_downsampled_sizes for more info about parameters.

    Returns
    -------
    int
        Number of downsampling steps.
    """
    nbytes = channel.handle.nbytes if isinstance(channel, Channel) else channel
    return len(calculate_approx_downsampled_sizes(nbytes, threshold, factor))
