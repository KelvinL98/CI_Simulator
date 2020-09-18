import numpy as np

def resample_tfm(tfm, analysis_rate, fs):
    output_factor = fs / analysis_rate

    if (output_factor == 1):
        num_samples_in = np.size(tfm, 2)
        num_samples_out = np.round(np.multiply(num_samples_in, output_factor))
        sample_points = range(0, num_samples_out)
        sample_indices = np.round(sample_points + 0.5)

        for i in range(0, np.size(tfm,2)):
            for j in range(0,np.size(sample_indices,2)):
                tfm[i][j] = sample_indices[j]
    return tfm
