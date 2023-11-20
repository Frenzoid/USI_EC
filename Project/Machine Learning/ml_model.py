#################### MODEL CREATION #####################################
from tensorflow import keras
import tensorflow as tf
import re
import hexdump
import tensorflow_model_optimization as tfmot

model = keras.Sequential()
model.add(keras.layers.Dense(1024, input_shape=(2,), activation="sigmoid"))
model.add(keras.layers.Dense(256, activation="sigmoid"))
model.add(keras.layers.Dense(1, activation=None))

model.compile(optimizer='adam',
              loss=keras.losses.MeanSquaredError(),
              metrics=[keras.metrics.MeanSquaredError()])

#################### DATA GENERATION #####################################
import numpy as np
def mahal_squared(x1, x2, Sigma_inv):
    delta = x1 - x2
    n = delta.shape[0]
    m = [delta[i:i+1].dot(Sigma_inv).dot(delta[i:i+1].T) for i in range(n)]
    return np.vstack(m)

def g(x, d):
    mu1 = 4 * np.ones((1, d))
    mu2 = 3 * np.ones((1, d))
    mu2[0, d//2:] /= 2
    mu3 = 2 * np.ones((1, d))
    mu3[0, d//2:] += 2
    Sigma_inv = np.eye(d)
    Sigma1_inv = np.eye(d)
    Sigma1_inv[d//2:, d//2:] += 1

    y = np.sqrt(3) * np.exp(- .5 * mahal_squared(x, 0, Sigma_inv)) + 0.6 * np.sin(2.2*x[:, 0]).reshape(-1, 1)
    y += - np.exp(-mahal_squared(x, mu1, Sigma1_inv))
    y += 4 * np.exp(- 2 * mahal_squared(x, mu2, Sigma_inv))
    y += - np.sqrt(12) * np.exp(-mahal_squared(x, mu3, Sigma1_inv))
    return y

def get_data(n, d=2, sigma=.2):
    x1 = np.random.rand(n//2, d) * 5
    x2 = np.random.randn(n - n//2, d) + 2.5
    x = np.concatenate((x1, x2), axis=0)

    y = g(x, d) + np.random.randn(n, 1)*sigma
    return x, y[:, 0]

x, y = get_data(2000, d=2, sigma=0.1)

model.fit(x,y)

#################### EXPORT MODEL #####################################
def dump_model(model: bytes, model_name: str = 'model') -> str:
  bytes = hexdump.dump(model).split(' ')
  c_array = ', '.join(['0x%02x' % int(byte, 16) for byte in bytes])
  c = 'const unsigned char %s[] DATA_ALIGN_ATTRIBUTE = {%s};' % (model_name, c_array)
  c += '\nconst int %s_len = %d;' % (model_name, len(bytes))
  preamble = '''
  #ifdef __has_attribute
  #define HAVE_ATTRIBUTE(x) __has_attribute(x)
  #else
  #define HAVE_ATTRIBUTE(x) 0
  #endif
  #if HAVE_ATTRIBUTE(aligned) || (defined(__GNUC__) && !defined(__clang__))
  #define DATA_ALIGN_ATTRIBUTE __attribute__((aligned(4)))
  #else
  #define DATA_ALIGN_ATTRIBUTE
  #endif
  '''
  c = preamble + c
  with open(f"{model_name}.h", "w") as f:
    f.write(c)
  return c

print(model.summary())