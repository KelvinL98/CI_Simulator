import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)

def resample_tfm(tfm, analysis_rate, fs):
    output_factor = fs / analysis_rate

    if (output_factor != 1):
        print(np.size(tfm,2))
        num_samples_in = np.size(tfm, 2)
        num_samples_out = np.round(np.multiply(num_samples_in, output_factor))
        #    sample_points   = (0:num_samples_out-1) / output_factor;
        sample_points = range(0, int(num_samples_out))
        sample_points = np.divide(sample_points, output_factor)

        sample_indices = np.round(np.add(sample_points, 0.5))

        offset = 0
        new_tfm = np.zeros([np.size(tfm,1),np.size(sample_indices)], dtype = np.double)
        ##replicate tfm = tfm(:, sample_indices);
        #go through all i ( 22 )rows
       # np.savetxt('sampleindices.csv', sample_indices, delimiter=',')
        for i in range(0, np.size(tfm,1)):
            #for each row fill out j ( 503856) columns.
            for j in range(0,np.size(sample_indices)):
                if (int(sample_indices[j])!= 0):
                    # sample indices goes from 0-2798 (2799 values) in matlab
                    # assuming that 0 means nothing, ignore those, otherwise offset by 1
                    #print(sample_indices[j])

                    new_val = np.double(tfm[0][i][int(sample_indices[j])-1])
                    #print(new_val)
                    #print(type(new_tfm[i][j]))
                    new_tfm[i][j] = new_val
                   # print(new_tfm[i][j])
    print(np.max(new_tfm))
    np.savetxt('tfm.csv', new_tfm, delimiter=',')
    return new_tfm
