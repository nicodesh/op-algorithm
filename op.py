import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def op(data, **kwargs):
    """ OP Algorithm. Returns a changepoints vector.
    Args:
        data (list): array-like, 1 dimension.
        B (float): penalty to apply.
    """
    
    # Preprocessing
    df = pd.DataFrame(data)
    df['squared'] = np.square(df[0])
    df['cumsum'] = np.cumsum(df[0], axis=0)
    df['cumsumsquared'] = np.cumsum(df['squared'], axis=0)
    df['diviseur'] = [x for x in range(1,len(df)+1)]
    df['mean'] = df['cumsum'] / df['diviseur']
    df['meansquared'] = np.square(df['mean'])
    df = df.append({
        0:0,'cumsum':0,
        'cumsumsquared':0,
        'diviseur':0,
        'mean':0,
        'meansquared':0,
        'squared':0}, ignore_index=True)
    
    if 'penalty' in kwargs:
        B = kwargs['penalty']
    else:
        B = 2 * np.log(len(data))
    
    F = [-B] # Actual cost
    CP = [-1] # Last segment position

    # Parse the data
    for pos, x in enumerate(data):

        # Parse all the Yi:pos
        costs = []
        min_cost_val_temp = float("inf")
        min_cost_pos_temp = -1
        for i in range(0,pos+1):
            # Square sum minus N times the square mean
            C = (df['cumsumsquared'].iloc[pos] - df['cumsumsquared'].iloc[i-1]) - (((pos+1) - (i+1) + 1) * ((data[i:pos+1].mean())**2))
            # Square sum = (df['cumsumsquared'].iloc[pos] - df['cumsumsquared'].iloc[i-1])
            # n = (pos+1) - (i+1) + 1
            # mean square = (data[i:pos+1].mean())**2)

            # Cost test
            temp_cost = F[i] + C + B
            if min_cost_val_temp > temp_cost:
                min_cost_val_temp = temp_cost
                min_cost_val_pos = i

        # Push the smallest cost
        F.append(min_cost_val_temp)

        # Push the position
        CP.append(min_cost_val_pos)
        
    return CP

def backtracking(CP):
    """ Apply backtracking to a CP vector from OP algorithm. Returns a "segments" vector.
    Args:
     CP: array-like 1 dimension.
    """

    # Data length
    n = len(CP)-1

    # Initialization
    segments = []
    changepoint = CP[n]

    # While the changepoint doesn't return the first point
    while changepoint > 0:

        segments.append(changepoint-1)
        changepoint = CP[changepoint]

    # The new vector was built with .append(), but since we parse from the end to the beginning,
    # We need to reverse it.
    segments.reverse()
    
    return segments

def plot_segments(data, segments, ylim=False):
    """ Plot segments generated by the OP & backtracking algorithms.
    Args:
        data: the data used to fit the model.
        segments: the segments returned by backtracking().
    """
    
    fig, ax = plt.subplots(figsize=(15,5))
    start = 0

    for end in segments:
        mean = data[start:end+1].sum() / len(data[start:end+1])
        plt.plot((start, end), (mean, mean))
        start = end+1

    end = len(data)-1
    mean = data[start:end+1].sum() / len(data[start:end+1])
    plt.plot((start, end), (mean, mean))
    
    if ylim != False:
        plt.ylim(ylim)
    plt.show()