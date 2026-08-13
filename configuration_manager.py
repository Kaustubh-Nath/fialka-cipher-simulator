import json
import os


class ConfigurationManager:

    CONFIG_FOLDER = "configs"


    @classmethod
    def initialize(cls):
        os.makedirs(cls.CONFIG_FOLDER, exist_ok=True)


    @classmethod
    def save(cls, engine, name):

        cls.initialize()

        data = {
            "version": "1.0",
            "machine": "Fialka Simulator",

            "rotor_order": engine.rotors.rotor_order,

            "positions": engine.rotors.positions,

            "card_reader": engine.card_reader.card,

            "reflector": engine.reflector.map
        }

        with open(
            os.path.join(cls.CONFIG_FOLDER, f"{name}.json"),
            "w"
        ) as file:

            json.dump(data, file, indent=4)


    @classmethod
    def list(cls):

        cls.initialize()

        return sorted(

            file[:-5]

            for file in os.listdir(cls.CONFIG_FOLDER)

            if file.endswith(".json")
        )


    @classmethod
    def load(cls, engine, name):

        with open(

            os.path.join(cls.CONFIG_FOLDER, f"{name}.json")

        ) as file:

            data = json.load(file)

        engine.rotors.rotor_order = data["rotor_order"]

        engine.rotors.positions = data["positions"]

        engine.card_reader.card = data["card_reader"]

        engine.reflector.map = data["reflector"]


    @classmethod
    def delete(cls, name):

        os.remove(

            os.path.join(

                cls.CONFIG_FOLDER,

                f"{name}.json"

            )
        )