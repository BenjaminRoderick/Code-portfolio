import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft2, ifft2
from scipy.ndimage import convolve
from scipy.signal import convolve2d

def gaussian_kernel(size, sigma):
    """
    #blur
    #choose size 3 5 7
    #sigma motion blur
    """
    
    ax = np.linspace(-(size // 2), size // 2, size)
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-(xx**2 + yy**2) / (2. * sigma**2))
    return kernel / np.sum(kernel)

def motion_blur_kernel(length=15, angle=0, alpha = 0.5):
    # Create coordinate grid
    ax = np.linspace(-(length // 2), length // 2, length)
    xx, yy = np.meshgrid(ax, ax)
    theta = np.deg2rad(angle)
    line = np.abs(xx * np.cos(theta) + yy * np.sin(theta)) < alpha
    kernel = line.astype(np.float32)
    kernel /= kernel.sum()
    return kernel

def project_onto_dual_iso_norm_unit_ball(y):
    """
    Projects y (with shape [..., 2]) onto the unit L2-ball at each pixel.
    Isotropic dual norm projection: y / max(1, ||y||_2).
    """
    # y[...,0], y[...,1] are the two components at each pixel
    mag = np.sqrt(y[...,0]**2 + y[...,1]**2)
    denom = np.maximum(mag, 1.0)  # clamp so that ||y|| <= 1
    # Avoid division by zero
    denom_safe = np.where(denom == 0, 1, denom)
    return y / denom_safe[..., np.newaxis]


def apply_periodic_conv2D(x, kernel):
    """
    Spatial-domain 2D convolution with periodic boundary conditions
    (wrap-around), using scipy.ndimage.convolve.
    """
    return convolve(x, kernel, mode='wrap')


def apply_periodic_conv2D_trans(x, kernel):
    """
    Transpose of the convolution with real kernel is just convolution
    with the flipped kernel (assuming real-valued kernel).
    """
    flipped_kernel = np.flipud(np.fliplr(kernel))
    return convolve(x, flipped_kernel, mode='wrap')


def apply_D(x):
    """
    Forward difference operator for TV in 2D, periodic boundary.
    Returns an array of shape (rows, cols, 2):
      - D[...,0] = vertical forward difference
      - D[...,1] = horizontal forward difference
    """
    rows, cols = x.shape
    Dx = np.zeros((rows, cols, 2), dtype=x.dtype)

    # vertical difference (downwards), wrap top to bottom
    Dx[..., 0] = np.roll(x, -1, axis=0) - x
    # horizontal difference (rightwards), wrap left to right
    Dx[..., 1] = np.roll(x, -1, axis=1) - x

    return Dx


def apply_D_trans(y):
    """
    Transpose of the forward difference (negative of the backward difference),
    summing across vertical and horizontal components.
    """
    # y has shape (rows, cols, 2)
    rows, cols, _ = y.shape
    # vertical component
    vt = -y[..., 0] + np.roll(y[..., 0], 1, axis=0)
    # horizontal component
    hz = -y[..., 1] + np.roll(y[..., 1], 1, axis=1)
    return vt + hz


def eval_iso_norm(y):
    """
    Evaluate the isotropic norm (sum of sqrt(dx^2 + dy^2)) over all pixels.
    y has shape (..., 2).
    """
    return np.sum(np.sqrt(y[..., 0]**2 + y[..., 1]**2))

def eigValsForPeriodicConvOp(kernel, numRows, numCols):
    """
    Compute the eigenvalues of the periodic convolution operator.
    The kernel is zero-padded to the desired size.
    """
    padded = np.zeros((numRows, numCols))
    kh, kw = kernel.shape
    padded[:kh, :kw] = kernel
    return fft2(padded)

def applyPeriodicConv2D(x, eigVals):
    """
    Apply a periodic convolution to x by multiplying the FFTs.
    """
    return np.real(ifft2(fft2(x) * eigVals))

def applyBlockCyclicConv2D(x, eigValArrs):
    """
    Apply block cyclic convolution. 
    eigValArrs is assumed to have shape (nr, nc, R, S).
    """
    nr, nc, R, S = eigValArrs.shape
    out = np.zeros_like(x)
    for r in range(R):
        for s in range(S):
            rowStart = r * nr
            rowStop = (r + 1) * nr
            colStart = s * nc
            colStop = (s + 1) * nc
            arr = eigValArrs[:, :, r, s]
            out[rowStart:rowStop, colStart:colStop] = np.real(
                ifft2(arr * fft2(x[rowStart:rowStop, colStart:colStop]))
            )
    return out

def solve_u(rhs, scaled_kernel): 
    """ Solve the linear system (I + KᵀK + DᵀD) u = rhs using FFT, assuming periodic boundary conditions."
        "Parameters:
    rhs           : 2D numpy array representing the right-hand side.
    scaled_kernel : 2D numpy array representing the scaled convolution kernel.

    Returns:
    u             : 2D numpy array solution.
    """
    # Get image dimensions
    numRows, numCols = rhs.shape

    # Compute the FFT of the scaled_kernel, padded to the image size.
    K_fft = np.fft.fft2(scaled_kernel, s=(numRows, numCols))
    # Compute the squared magnitude |K_fft|^2 element-wise.
    K_abs2 = np.abs(K_fft)**2

    # Create frequency grids for rows and columns.
    fx = np.fft.fftfreq(numRows)
    fy = np.fft.fftfreq(numCols)
    # Note: meshgrid is used with (fy, fx) ordering so that FX corresponds to columns.
    FX, FY = np.meshgrid(fy, fx)

    # Compute eigenvalues for DᵀD under periodic BCs using forward differences.
    # Here, the eigenvalues are L = 4*(sin(π·FX)^2 + sin(π·FY)^2).
    L = 4 * (np.sin(np.pi * FX)**2 + np.sin(np.pi * FY)**2)

    # Form the denominator in the Fourier domain: 1 + |K_fft|^2 + L.
    denom = 1 + K_abs2 + L

    # Compute the FFT of the right-hand side.
    rhs_fft = np.fft.fft2(rhs)
    # Solve for u in the Fourier domain.
    u_fft = rhs_fft / denom
    # Transform back to the spatial domain and take the real part.
    u = np.real(np.fft.ifft2(u_fft))
    return u

def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])

def eigValArrForCyclicConvOp(kernel, numRows, numCols):
    """
    Compute the eigenvalues of the cyclic convolution operator.
    The kernel is zero-padded to the desired size.
    """
    a = np.zeros((numRows, numCols), dtype=complex)

    a[0][0] = 1
    ra = convolve2d(a, kernel, mode='same', boundary='wrap')
    return np.conjugate(fft2(ra))

def applyCyclicConv2D(x, eigValArr):
    return ifft2(fft2(x) * eigValArr)
