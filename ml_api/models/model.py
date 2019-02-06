from joblib import load
import numpy as np
from threading import Thread


class Model:
    def __init__(self, file_name):
        self.__file_name = file_name
        self.__is_ready = False
        self.__model = None
        self.__meta_data = None

    def file_name(self):
        """Name of the model file."""
        return self.__file_name

    def is_ready(self):
        """Readiness of the model."""
        return self.__is_ready

    def meta_data(self):
        """Model meta data."""
        return self.__meta_data

    def __load_model(self):
        """Loads the model and sets __is_ready."""
        loaded = load(self.__file_name)
        self.__model = loaded['model']
        self.__meta_data = loaded['metadata']
        self.__is_ready = True

    def load_model(self):
        """Load the model in a Thread."""
        Thread(target=self.__load_model).start()

    def predict(self, features):
        """
        Create a prediction.

        :param features: features to send the model.
        :return: prediction
        """
        if not self.is_ready():
            raise RuntimeError("Model is not ready yet")

        model_input = np.asarray(features).reshape(1, -1)
        result = self.__model.predict(model_input)
        return int(result[0])
