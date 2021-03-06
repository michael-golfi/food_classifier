import logging
import functools

from keras.models import Sequential
from keras import layers
from keras.layers.normalization import BatchNormalization
from keras.applications import MobileNet, VGG16

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
file_handler = logging.FileHandler('./logs/models.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

__author__ = 'Junior Teudjio'
__all__ = ['base_model', 'mobilenet_model']


def base_model(init='glorot_uniform', activation='relu', batch_norm=True, dropout=0.5, regularizer='l2-0.01'):
    '''
    Create an instance of the baseline model.

    Parameters
    ----------
    init: str
        Weights initialization strategy.
    activation : str
        Activation function to use.
    batch_norm : boolean
        Whether to use batch normalization or not.
    dropout : float
        Ratio of weights to turn off before the final activation function
    regularizer: str : reg_type-reg_value
        Type and value of regularization to use, reg_type = l2 or l1

    Returns:
        model: Sequential()
            The baseline model object
    '''
    reg_type, reg_value = regularizer.split('-')
    if reg_type == 'l2':
        regularizer = layers.regularizers.l2(float(reg_value))
    else:
        regularizer = layers.regularizers.l1(float(reg_value))
    myConv2D = functools.partial(layers.Conv2D, kernel_initializer=init, kernel_regularizer=regularizer)
    
    model = Sequential()
    model.add(myConv2D(32, (3, 3), input_shape=(150, 150, 3)))
    if batch_norm:
        model.add(BatchNormalization())
    model.add(layers.Activation(activation))
    model.add(layers.MaxPooling2D((2, 2)))

    model.add(myConv2D(64, (3, 3)))
    if batch_norm:
        model.add(BatchNormalization())
    model.add(layers.Activation(activation))
    model.add(layers.MaxPooling2D((2, 2)))

    model.add(myConv2D(128, (3, 3)))
    if batch_norm:
        model.add(BatchNormalization())
    model.add(layers.Activation(activation))
    model.add(layers.MaxPooling2D((2, 2)))

    model.add(myConv2D(128, (3, 3)))
    if batch_norm:
        model.add(BatchNormalization())
    model.add(layers.Activation(activation))
    model.add(layers.MaxPooling2D((2, 2)))


    model.add(layers.Flatten())
    model.add(layers.Dropout(dropout))
    model.add(layers.Dense(512, activation=activation, kernel_initializer=init, kernel_regularizer=regularizer))
    model.add(layers.Dense(1, activation='sigmoid'))

    logger.info('''
    
    Created baseline model with params:
        init = {init}
        activation = {activation}
        batch_norm = {batch_norm}
        dropout = {dropout} 
        architecture = {architecture}'''.format(
        init=init,
        activation=activation,
        batch_norm=batch_norm,
        dropout=dropout,
        architecture = model.to_json()
    ))

    return model

# def pop(self):
#     '''Removes a layer instance on top of the layer stack.
#     '''
#     if not self.outputs:
#         raise Exception('Sequential model cannot be popped: model is empty.')
#     else:
#         self.layers.pop()
#         if not self.layers:
#             self.outputs = []
#             self.inbound_nodes = []
#             self.outbound_nodes = []
#         else:
#             self.layers[-1].outbound_nodes = []
#             self.outputs = [self.layers[-1].output]
#         self.built = False

def mobilenet_model(init='glorot_uniform', activation='relu', dropout=0.5, regularizer='l2-0.01'):
    '''
       Create an instance of the baseline model.

       Parameters
       ----------
       init: str
           Weights initialization strategy.
       activation : str
           Activation function to use.
       batch_norm : boolean
           Whether to use batch normalization or not.
       dropout : float
           Ratio of weights to turn off before the final activation function
       regularizer: str : reg_type-reg_value
           Type and value of regularization to use, reg_type = l2 or l1

       Returns:
           model: Sequential()
               The baseline model object
       '''
    reg_type, reg_value = regularizer.split('-')
    if reg_type == 'l2':
        regularizer = layers.regularizers.l2(float(reg_value))
    else:
        regularizer = layers.regularizers.l1(float(reg_value))
    myConv2D = functools.partial(layers.Conv2D, kernel_initializer=init, kernel_regularizer=regularizer)

    mobnet_base = MobileNet(weights='imagenet',
                          include_top=False,
                          input_shape=(160, 160, 3))
    # Since the mobilenet model was trained on Imagenet which doesn't contains much food images
    # We will drop some layers drop many (actually 20) deepest layers to ensure that mobilenet only extract
    # low level features like edges, basic shapes etc ...
    #for _ in xrange(20): pop(mobnet_base)
    ##### hum huuum: the above does not works, get key-error on final layer when saving model


    # now we freeze it
    mobnet_base.trainable = False

    # we create the complete network by appending randomly initialized layers
    model = Sequential()
    model.add(mobnet_base)

    model.add(myConv2D(128, (3, 3)))
    model.add(BatchNormalization())
    model.add(layers.Activation(activation))
    model.add(layers.MaxPooling2D((2, 2)))


    model.add(layers.Flatten())
    model.add(layers.Dropout(dropout))
    model.add(layers.Dense(256, activation=activation, kernel_initializer=init, kernel_regularizer=regularizer))
    model.add(layers.Dense(1, activation='sigmoid'))

    logger.info('''

        Created mobilenet model with params:
            init = {init}
            activation = {activation}
            dropout = {dropout} 
            architecture = {architecture}
            '''.format(
        init=init,
        activation=activation,
        dropout=dropout,
        architecture=model.to_json()
    ))
    return model


if __name__ == '__main__':
    mobilenet_model().summary()