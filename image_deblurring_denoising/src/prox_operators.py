import numpy as np

def soft_threshold(x, alpha):
    """Componentwise soft-threshold at level alpha."""
    return np.sign(x) * np.maximum(np.abs(x) - alpha, 0.0)

def prox_l1(z, t):
    """
    Proximal operator of t * ||x||_1.
    
    Solves:
        min_x  (1/2)*||x - z||^2  +  t * ||x||_1
        
    The closed-form solution is the soft-thresholding:
        x_i = sign(z_i) * max(|z_i| - t, 0).
        
    Parameters
    ----------
    z : np.ndarray
        Input array (can be 1D or multi-dimensional).
    t : step
        Nonnegative regularization/threshold parameter.
        
    Returns
    -------
    x : np.ndarray
        The result of applying prox_{t ||·||_1}(z).
    """
    return np.sign(z) * np.maximum(np.abs(z) - t, 0.0)

def prox_l2_norm_squared(z, t):
    """
    Proximal operator of t * ||x||_2^2.
    
    Solves:
        min_x  (1/2)*||x - z||^2  +  t * ||x||_2^2
        
    The closed-form solution is:
        x = (1/(1 + 2*t)) * z.
        
    Parameters
    ----------
    z : np.ndarray
        Input array (can be 1D or multi-dimensional).
    t : step
        Nonnegative regularization/threshold parameter.
        
    Returns
    -------
    x : np.ndarray
        The result of applying prox_{t ||·||_2^2}(z).
    """
    return z / (1 + t)
    #return z / (1 + 2 * t)
    #return z * (2 + 1/t)/t
    #return z * np.maximum(0.0, 1.0 - t / np.linalg.norm(z, ord=2))


def prox_tv_iso(z2, z3, t_gamma):
    """
    Proximal operator of t_gamma * sum_i sqrt(z2(i)^2 + z3(i)^2).
    
    Parameters
    ----------
    z2 : np.ndarray
        The 'horizontal' component array of shape [...], same shape as z3.
    z3 : np.ndarray
        The 'vertical' component array, same shape as z2.
    t_gamma : float
        Nonnegative threshold parameter.
        
    Returns
    -------
    y2, y3 : np.ndarray
        The result of applying prox_{t_gamma ||·||_2} to each pixel's (z2(i), z3(i)).
        Same shape as z2, z3.
    """
    # Compute norms
    norms = np.sqrt(z2**2 + z3**2)
    
    # Avoid division by zero
    # scale = max(0, 1 - t_gamma/norms)
    # but only where norms > 0
    # dont mind the warning please
    
    # scale = np.where(norms > 0, np.maximum(0.0, 1.0 - t_gamma / norms), 0.0)
    np.seterr(divide='ignore', invalid='ignore')  # Ignore divide by zero warnings
    scale = np.maximum(0.0, 1.0 - t_gamma / norms)
    scale[norms < 0] = 0 # (eliminate 0 and less)

    # print("norm", norms)
    y2 = scale * z2
    y3 = scale * z3

    return y2, y3