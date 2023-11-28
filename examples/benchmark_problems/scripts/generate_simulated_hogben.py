import numpy as np
import pickle
import os

from hogben.models.samples import simple_sample, many_param_sample, \
    thin_layer_sample_1, thin_layer_sample_2, similar_sld_sample_1, \
    similar_sld_sample_2
from hogben.simulate import simulate

angle_times = [(0.7, 100, 5),
               (2.0, 100, 20)]

data_path = f'{os.path.dirname(__file__)}/../HOGBEN_samples/data/'
model_path = f'{os.path.dirname(__file__)}/../HOGBEN_samples/Models/'
problem_path = f'{os.path.dirname(__file__)}/../HOGBEN_samples/'

def generate_data_and_model(sample):

    model, data = simulate(sample.structure, angle_times)

    # save data to txt file
    np.savetxt(os.path.join(data_path, f"{sample.name}.txt"), data[:,[0,1,3]], header='X Y E')

    # save model
    with open(os.path.join(model_path, f"{sample.name}_model.pkl"), 'wb+') as f:
        pickle.dump(model, f)

def write_problem(sample_name, description):
    with open(f'{problem_path}/{sample_name}.txt', 'w') as f:
            f.write('# FitBenchmark Problem\n')
            f.write("software = 'HOGBEN'\n")
            f.write(f"name = '{sample_name}'\n")
            f.write(f"description = '{description}'\n")
            f.write(f"input_file = '{sample_name}.txt'\n")
            f.write(f"function = 'function={sample_name}_model.pkl'\n")
            f.write("plot_scale = 'logY'")

# 2-layer simple sample
simple = simple_sample()
description = "2-layer simple sample"
generate_data_and_model(simple)
write_problem(simple.name, description)

# 5-layer sample with many parameters
many_param = many_param_sample()
description = "5-layer sample with many parameters"
generate_data_and_model(many_param)
write_problem(many_param.name, description)

# 2-layer sample with thin layers
thin_layer1 = thin_layer_sample_1()
description = "2-layer sample with thin layers"
generate_data_and_model(thin_layer1)
write_problem(thin_layer1.name, description)

# 3-layer sample with thin layers
thin_layer2 = thin_layer_sample_2()
description = "3-layer sample with thin layers"
generate_data_and_model(thin_layer2)
write_problem(thin_layer2.name, description)

# 2-layer sample with layers of similar SLD
similar_sld1 = similar_sld_sample_1()
description = "2-layer sample with layers of similar SLD"
generate_data_and_model(similar_sld1)
write_problem(similar_sld1.name, description)

# 3-layer sample with layers of similar SLD
similar_sld2 = similar_sld_sample_2()
description = "3-layer sample with layers of similar SLD"
generate_data_and_model(similar_sld2)
write_problem(similar_sld2.name, description)

