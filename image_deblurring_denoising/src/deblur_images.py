import numpy as np
import matplotlib.pyplot as plt
from skimage import io, util, transform
from scipy.signal import convolve2d
from scipy.fft import fft2, ifft2
from argparse import ArgumentParser
import os.path
import json
import time

from basic_operations import solve_u, apply_D, apply_D_trans, apply_periodic_conv2D, apply_periodic_conv2D_trans, gaussian_kernel, motion_blur_kernel, rgb2gray
from basic_operations import eigValArrForCyclicConvOp, applyCyclicConv2D, eval_iso_norm
from prox_operators import prox_l1, prox_tv_iso, prox_l2_norm_squared


def run_deblurring(fname, problem, algorithm, kernel_type, params_dict, path, show_intermediate):
    # Unpack parameters
    try:
        kernel_size  = int(params_dict['kernel_size'])
        resize_factor = float(params_dict['resize_factor'])
        noise_density = float(params_dict['noise_density'])
        noise_type  = params_dict['noise_type']
        if kernel_type == 'gaussian':
            sigma = float(params_dict['sigma'])
        elif kernel_type == 'motion_blur':
            angle = float(params_dict['angle'])
            alpha = float(params_dict['alpha'])
    except:
        raise ValueError("Missing or invalid parameters in the parameters file.")
    
    # Prepare the Gaussian kernel with the current sigma
    if kernel_type == 'gaussian':
        kernel = gaussian_kernel(kernel_size, sigma)
    elif kernel_type == 'motion_blur':
        kernel = motion_blur_kernel(kernel_size, angle, alpha)
    else:
        raise ValueError(f"Unknown kernel type: {kernel_type}")

    # Read and preprocess image
    if(not os.path.isfile(os.path.join(path[:-3] + 'images', fname))):
        raise FileNotFoundError(f"Image file {fname} not found.\nMake sure to store the image in the \"images\" folder.")

    I = io.imread(os.path.join(path[:-3] + 'images', fname))
    if I.ndim == 3:
        I = rgb2gray(I)
    I = I.astype(np.float64)
    I = transform.resize(I, (int(I.shape[0] * resize_factor), int(I.shape[1] * resize_factor)), anti_aliasing=True)
    I = (I - I.min()) / (I.max() - I.min())

    # Blur image and add noise
    b = convolve2d(I, kernel, mode='same', boundary='wrap')
    if noise_type == 'gaussian':
        b = util.random_noise(b, mode='gaussian', mean=0, var=noise_density**2)
    elif noise_type == 's&p':
        b = util.random_noise(b, mode='s&p', amount=noise_density)
    else:
        raise ValueError(f"Unknown noise type: {noise_type}")

    if(show_intermediate):
        plt.figure()
        plt.title("Image Before Blurring")
        plt.imshow(I, cmap='gray')
        plt.axis('off')

        plt.figure()
        plt.title("Blurred Image")
        plt.imshow(b, cmap='gray')
        plt.axis('off')
        plt.show(block=False)


    start_time = time.time()
    if(algorithm == 'douglasrachfordprimal'):#douglas-rachford primal algorithm
        costs, final_image = deblur_simpleTV_DR(b, kernel, problem, params_dict)
    elif(algorithm == 'douglasrachfordprimaldual'):#douglas-rachford primal-dual algorithm
        costs, final_image = deblur_simpleTV_DR_PD(b, kernel, problem, params_dict)
    elif(algorithm == 'admm'):#ADMM algorithm
        costs, final_image = deblur_ADMM(b, kernel, problem, params_dict)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    
    elapsed_time = time.time() - start_time
    
    # For the purpose of grid search, we use the final cost as our metric
    return costs, elapsed_time, final_image


def deblur_simpleTV_DR(b, kernel, problem, params_dict):#Douglas-Rachford primal algorithm
    # Unpack parameters
    try:
        mu          = float(params_dict['mu'])
        t           = float(params_dict['t'])
        gamma       = float(params_dict['gamma'])
        s           = float(params_dict['s'])
        rho   = float(params_dict['rho'])
        max_iter     = int(params_dict['max_iter'])
    except:
        raise ValueError("Missing or invalid parameters in the parameters file.")
    
    beta = np.sqrt(s / t)

    # Scale kernel and data
    scaled_kernel = kernel * beta
    scaled_b      = b * beta
    scaled_mu     = mu / beta

    numRows, numCols = b.shape

    # Initialize primal variable and dual variable (3 channels: channel 0 for fidelity, channels 1-2 for TV)
    p_x = scaled_b.copy()
    p_z = np.zeros((numRows, numCols, 3))

    costs = []
    unchanged_counter = 0
    divergence_counter = 0

    for k in range(max_iter):
        # Proximal operators
        # x-prox: project onto [0,1]
        xk = np.clip(p_x, 0, 1)

        if(problem == 'l1'): # Fidelity prox (first channel)
            y1 = scaled_b + prox_l1(p_z[...,0] - scaled_b, t)
        elif(problem == 'l2'):
            y1 = scaled_b + prox_l2_norm_squared(p_z[...,0] - scaled_b, t)# this does not work at the moment
            #y1 = prox_l2_norm_squared(p_z[...,0], t)
        else:
            raise ValueError(f"Unknown problem type: {problem}")

        # TV norm prox (channels 2 and 3)
        z2 = p_z[...,1]  # second channel
        z3 = p_z[...,2]  # third channel
        y2, y3 = prox_tv_iso(z2, z3, t*gamma )

        # Combine into the three-channel y_k 
        yk = np.stack([y1, y2, y3], axis=-1)

        # Compute u and v 
        # Compute Aᵀ(2y_k - p_z)
        temp_f = 2 * yk[...,0] - p_z[...,0] # for norm l1, shape (numRows, numCols, 1)
        At_temp_f = apply_periodic_conv2D_trans(temp_f, scaled_kernel)
        temp_tv = 2 * yk[...,1:] - p_z[...,1:]  # for TV, shape (numRows, numCols, 2) not (numRows, numCols, 3) 
        At_temp_tv = apply_D_trans(temp_tv)
        At_term = At_temp_f + At_temp_tv

        # Right-hand side for u update: 2xk - p_x + Aᵀ(2y_k - p_z)
        rhs = 2 * xk - p_x + At_term
        u = solve_u(rhs, scaled_kernel)

        # Compute v = A(u) = [K*u; D*u]
        v1 = apply_periodic_conv2D(u, scaled_kernel)  # fidelity part
        v2 = apply_D(u)  # TV part, should return two channels
        vk = np.concatenate([v1[..., np.newaxis], v2], axis=-1)  # shape (numRows, numCols, 3)

        # over-relaxation updates
        p_x = p_x + rho * (u - xk)
        p_z = p_z + rho * (vk - yk)

        # Cost tracking
        residual = apply_periodic_conv2D(xk, scaled_kernel) - scaled_b
        # Dx = apply_D(xk)        
        cost =  scaled_mu * np.mean(np.abs(residual))
        #norm with out t
        costs.append(cost)

        if k != 0:
            if costs[-2] - cost < 1e-5:
                unchanged_counter += 1
                if unchanged_counter >= 10:
                    print(f"Stopping criterion met at iteration {k + 1}.")
                    break
            else:
                unchanged_counter = 0
            if costs[-2] + 1e-5 < cost:
                divergence_counter += 1
                if divergence_counter >= 10:
                    print(f"Divergence detected at iteration {k + 1}.")
                    break
            else:
                divergence_counter = 0

    # Final estimate: project final u onto [0,1]
    final_image = np.clip(u, 0, 1)

    return costs, final_image

def deblur_simpleTV_DR_PD(b, kernel, problem, params_dict):#Douglas-Rachford primal-dual algorithm
    # Unpack parameters
    try:
        mu          = float(params_dict['mu'])#in the paper, mu = 1/gamma
        t           = float(params_dict['t'])
        gamma       = float(params_dict['gamma'])
        s           = float(params_dict['s'])
        rho   = float(params_dict['rho'])
        max_iter     = int(params_dict['max_iter'])
    except:
        raise ValueError("Missing or invalid parameters in the parameters file.")
    
    beta = np.sqrt(s / t)

    # Scale kernel and data
    scaled_kernel = kernel * beta
    scaled_b      = b * beta
    scaled_mu     = mu / beta

    numRows, numCols = b.shape

    eigValArr_kernel = eigValArrForCyclicConvOp(scaled_kernel, numRows, numCols)
    eigValArr_Dupper = eigValArrForCyclicConvOp(np.array([[-1 * beta],[beta]]), numRows, numCols)#beta*[-1,1]T
    eigValArr_Dlower = eigValArrForCyclicConvOp(np.array([[-1 * beta, beta]]), numRows, numCols)#beta*[-1,1]
    kernel_conj_product = t**2 * np.conjugate(eigValArr_kernel) * eigValArr_kernel
    Dupper_conj_product = t**2 * np.conjugate(eigValArr_Dupper) * eigValArr_Dupper
    Dlower_conj_product = t**2 * np.conjugate(eigValArr_Dlower) * eigValArr_Dlower

    eigValMatrix = kernel_conj_product + Dupper_conj_product + Dlower_conj_product + np.ones((numRows, numCols))

    p_x = scaled_b.copy()
    p_z = np.zeros((numRows, numCols, 3))

    costs = []
    unchanged_counter = 0
    divergence_counter = 0

    for k in range(max_iter):
        #compute resolvents
        # Proximal operators
        # x-prox: project onto [0,1]
        x_k = np.clip(p_x, 0, 1)

        if(problem == 'original'):
            y1 = np.clip(p_z[...,0] - t * scaled_b, -1 * scaled_mu, scaled_mu)
        elif(problem == 'l1'): # Fidelity prox (first channel)
            y1 = scaled_b + prox_l1(p_z[...,0] - scaled_b, t)#l1 penalty
        elif(problem == 'l2'):
            y1 = scaled_b + prox_l2_norm_squared(p_z[...,0] - scaled_b, t)#l2 penalty
        else:
            raise ValueError(f"Unknown problem type: {problem}")

        # TV norm prox (channels 2 and 3)
        y2, y3 = prox_tv_iso(p_z[...,1], p_z[...,2], t*gamma )

        y1_term = 2 * y1 - p_z[...,0]
        y2_term = 2 * y2 - p_z[...,1]
        y3_term = 2 * y3 - p_z[...,2]#2zk - p(k-1)

        apply_y1 = applyCyclicConv2D(y1_term, np.conjugate(eigValArr_Dupper))
        apply_y2 = applyCyclicConv2D(y2_term, np.conjugate(eigValArr_Dupper))
        apply_y3 = applyCyclicConv2D(y3_term, np.conjugate(eigValArr_Dlower))

        rhs = (2 * x_k - p_x) - t * (apply_y1 + apply_y2 + apply_y3)
        w_k = ifft2(fft2(rhs) / eigValMatrix)

        v_k1 = y1_term + t * applyCyclicConv2D(w_k, eigValArr_kernel)
        v_k2 = y2_term + t * applyCyclicConv2D(w_k, eigValArr_Dupper)
        v_k3 = y3_term + t * applyCyclicConv2D(w_k, eigValArr_Dlower)


        p_x = p_x + rho * (w_k - x_k)
        q_1 = p_z[...,0] + rho * (v_k1 - y1)
        q_2 = p_z[...,1] + rho * (v_k2 - y2)
        q_3 = p_z[...,2] + rho * (v_k3 - y3)

        p_z = np.stack([q_1, q_2, q_3], axis=-1)# p_z for next iteration

        residual = apply_periodic_conv2D(x_k, scaled_kernel) - scaled_b
        # Dx = apply_D(xk)        
        cost =  scaled_mu * np.mean(np.abs(residual))
        #norm with out t
        costs.append(cost)

        if k != 0:
            if costs[-2] - cost < 1e-5:
                unchanged_counter += 1
                if unchanged_counter >= 10:
                    print(f"Stopping criterion met at iteration {k + 1}.")
                    break
            else:
                unchanged_counter = 0
            if costs[-2] + 1e-5 < cost:
                divergence_counter += 1
                if divergence_counter >= 10:
                    print(f"Divergence detected at iteration {k + 1}.")
                    break
            else:
                divergence_counter = 0
    
    # Final estimate: project final w_k onto [0,1]
    final_image = np.clip(np.real(w_k), 0, 1)

    return costs, final_image

def deblur_ADMM(b, kernel, problem, params_dict):
    # Unpack parameters
    try:
        t       = float(params_dict['t'])
        rho     = float(params_dict['rho'])
        mu      = float(params_dict['mu'])
        gamma   = float(params_dict['gamma'])
        max_iter = int(params_dict['max_iter'])
    except:
        raise ValueError("Missing or invalid parameters in the parameters file.")
    
    # Initialize variables x0, u0, y0, w0, z0
    x = b.copy()
    u = x.copy()
    Ax = apply_periodic_conv2D(x, kernel)
    Dx = apply_D(x)  # returns two-channel gradient
    y = np.concatenate([Ax[..., np.newaxis], Dx], axis=-1)
    w = np.zeros_like(u)
    z = np.zeros_like(y)

    costs = []

    for k in range(max_iter):
        # x-update
        ATy = apply_periodic_conv2D_trans(y[...,0], kernel) + apply_D_trans(y[...,1:])
        ATz = apply_periodic_conv2D_trans(z[...,0], kernel) + apply_D_trans(z[...,1:])
        rhs = u + ATy - (1.0/t) * (w + ATz)
        x = solve_u(rhs, kernel)

        #  u-update prox
        u = np.clip(rho * x + (1 - rho) * u + w/t, 0, 1)

        # y-update
        Ax = apply_periodic_conv2D(x, kernel)
        Dx = apply_D(x)
        Aconcat = np.concatenate([Ax[..., np.newaxis], Dx], axis=-1)
        temp = rho * Aconcat + (1 - rho) * y + z/t
        if(problem == 'l1'):
            # fidelity prox on channel 0 (l1 around b)
            y0 = b + prox_l1(temp[...,0] - b, mu/t)
        elif(problem == 'l2'):
            y0 = b + prox_l2_norm_squared(temp[...,0] - b, mu/t)
        else:
            raise ValueError(f"Unknown problem type: {problem}")
        
        # TV prox on channels 1-2
        y2, y3 = prox_tv_iso(temp[...,1], temp[...,2], gamma/t)
        y = np.stack([y0, y2, y3], axis=-1)

        # w-update
        w = w + t * (x - u)
        # z-update
        Ax = apply_periodic_conv2D(x, kernel)
        Dx = apply_D(x)
        Aconcat = np.concatenate([Ax[..., np.newaxis], Dx], axis=-1)
        z = z + t * (Aconcat - y)

        # Cost
        residual = apply_periodic_conv2D(x, kernel) - b
        cost = mu * np.mean(np.abs(residual))
        costs.append(cost)

    # xSol = (I + A^T A)^{-1}(u + A^T y - 1/t(w + A^T z))
    ATy = apply_periodic_conv2D_trans(y[...,0], kernel) + apply_D_trans(y[...,1:])
    ATz = apply_periodic_conv2D_trans(z[...,0], kernel) + apply_D_trans(z[...,1:])
    final_rhs = u + ATy - (1.0/t) * (w + ATz)
    xSol = solve_u(final_rhs, kernel)
    xSol = np.clip(xSol, 0, 1)

    return xSol, costs


def run_grid_search(fname, problem, algorithm, kernel, params_dict, path):
    # ranges for t and gamma 

    t_values = np.linspace(0.01, 2, 10)      
    gamma_values = np.linspace(1, 20, 10)      
    
    results = {} 
    
    for t_val in t_values:
        for gamma_val in gamma_values:
            # Update the parameters for this iteration
            params_dict['t'] = t_val
            params_dict['gamma'] = gamma_val
            
            # print(f"Running grid search for t = {t_val:.2f} and sigma = {sigma_val:.2f}...")
            print(f"Running grid search for t = {t_val:.2f} and gamma = {gamma_val:.2f}...")
            costs, elapsed_time, final_image = run_deblurring(fname, problem, algorithm, kernel, params_dict, path, False)
            final_cost = costs[-1]  # Use the last cost as the final cost
            #very inefficient at the moment
            results[(t_val, gamma_val)] = final_cost
            print(f"    Final cost: {final_cost:.5f} (elapsed time: {elapsed_time:.2f} sec)")
    
    
    return results

def loss_function():#todo update this
    pass

def main(parameters_file, problem, algorithm, kernel, fname, store_results, grid_search, show_end):
    path = os.path.dirname(os.path.abspath(__file__))#get the path of the src folder

    if(not os.path.isfile(os.path.join(path, parameters_file))):
        raise FileNotFoundError(f"Parameters file {parameters_file} not found.\nMake sure to put the parameters file in the src directory.")
    elif(not (parameters_file.endswith('.csv') or parameters_file.endswith('.json'))):
        raise ValueError(f"Parameters file must be a .csv or .json file.")
    
    params_dict = {}
    if(parameters_file.endswith('.json')):#load all parameters from the file into a dictionary
        with open(os.path.join(path, parameters_file), 'r') as f:
            params_dict = json.load(f)
    elif(parameters_file.endswith('.csv')):
        with open(os.path.join(path, parameters_file), 'r') as f:
            for line in f:
                line_tuple = line.rstrip().split(',')
                if len(line_tuple) == 2:
                    params_dict[line_tuple[0]] = line_tuple[1].strip().strip("'")#remove whitespaces and quotes
                else:
                    raise ValueError(f"Invalid line in parameters file: {line}")
    
    if(store_results):
        if(not os.path.exists(path[:-3] + 'out')):#check if the output directory exists, if not create it
            os.makedirs(path[:-3] + 'out')
        savetime = time.time()
        output = [savetime, algorithm, kernel, problem]
        outpath = os.path.join(path[:-3] + 'out', f'{savetime}_{fname.split(".")[0]}_results.txt')

    if(grid_search):# Run grid search over t and gamma
        results = run_grid_search(fname, problem, algorithm, kernel, params_dict, path)
        t_vals = sorted(set(key[0] for key in results.keys()))
        gamma_vals = sorted(set(key[1] for key in results.keys()))
        cost_matrix = np.zeros((len(gamma_vals), len(t_vals)))

        # Find best parameter combination (minimizing final cost)
        best_params = min(results, key=results.get)
        best_cost = results[best_params]
        best_string = f"\nBest parameters found: t = {best_params[0]:.2f}, gamma = {best_params[1]:.2f} with cost = {best_cost:.5f}\nt,gamma,cost"
        print(best_string)
        if(store_results):
            output.append(best_string)

        for i, gamma_val in enumerate(gamma_vals):
            for j, t_val in enumerate(t_vals):
                cost_matrix[i, j] = results[(t_val, gamma_val)]
                if(store_results):
                    output.append(f"{t_val:.2f},{gamma_val:.2f},{cost_matrix[i, j]:.5f}")
        
        plt.figure()
        plt.imshow(cost_matrix, extent=[t_vals[0], t_vals[-1], gamma_vals[0], gamma_vals[-1]],
                origin='lower', aspect='auto')
        plt.colorbar(label='Final cost')
        plt.xlabel('t values')
        plt.ylabel('gamma values')
        plt.title('Grid Search: Final Cost for Different t and sigma')
        plt.show(block=False)



        if(store_results):
            plt.savefig(os.path.join(path[:-3] + 'out', f'{savetime}_{fname.split(".")[0]}_gs_{problem}_{algorithm}_{kernel}.png'))
    else:
        # Run the deblurring algorithm
        costs, elapsed_time, final_image = run_deblurring(fname, problem, algorithm, kernel, params_dict, path, True)
        final_cost = costs[-1]
        print(f"Final cost: {final_cost:.5f} (elapsed time: {elapsed_time:.2f} sec)")

        if(store_results):
            output.append(f"\nFinal cost: {final_cost:.5f} (elapsed time: {elapsed_time:.2f} sec)\nCost history:\niteration,cost")
            for i, cost in enumerate(costs):
                output.append(f"{i + 1},{cost:.5f}")

        plt.figure()
        plt.imshow(final_image, cmap='gray')
        plt.title("Deblurred Image")
        plt.axis('off')
        plt.show(block=False)

        max_iter = len(costs)
        plt.figure()
        plt.title("Cost Function Over Iterations")
        plt.plot(np.arange(0, max_iter, 1),costs)

        if(store_results):
            plt.savefig(os.path.join(path[:-3] + 'out', f'{savetime}_{fname.split(".")[0]}_costHistory_{problem}_{algorithm}_{kernel}.png'))

    if(store_results):
        with open(outpath, 'w') as f:
            for key, value in params_dict.items():
                f.write(f"{key}: {value}\n")
            for line in output:
                f.write(str(line) + '\n')
        print(f"Results stored in {outpath}")

    if(show_end):
        plt.show()

if __name__ == '__main__':
    parser = ArgumentParser(description="Image Deblurring")
    parser.add_argument('problem', type=str, nargs='?', default='l1', help="Problem type: 'l1' OR 'l2'")
    parser.add_argument('algorithm', type=str, nargs='?', default='douglasrachfordprimal', help="Algorithm type: douglasrachfordprimal OR douglasrachfordprimaldual")
    parser.add_argument('filename', type=str, nargs='?', default='manWithHat.tiff', help="Filename of the input image")
    parser.add_argument('kernel', type=str, nargs='?', default='gaussian', help="Name of the kernel type")
    parser.add_argument('parameters_file', nargs='?', default='default_parameters.csv', type=str, help="Name of the parameters file")
    parser.add_argument('-g', '--grid_search', action='store_true', help="Perform grid search for gamma and t parameters")
    parser.add_argument('-s', '--store_results', action='store_true', help="Store results in a file")
    args = parser.parse_args()

    parameters_file = args.parameters_file
    problem = args.problem
    algorithm = args.algorithm
    kernel = args.kernel
    fname = args.filename
    store_results = args.store_results
    grid_search = args.grid_search

    main(parameters_file, problem, algorithm, kernel, fname, store_results, grid_search, True)