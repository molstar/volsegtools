from volsegtools._storage.channel import Channel


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
