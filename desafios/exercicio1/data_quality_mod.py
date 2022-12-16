import json

class DataQuality:
    def __init__(self, json_schema):
        """
        Description
            Constructor method. Initialize when the class is instanciated.
        Args
            json_schema (String): A path of the JSON schema.
            event (String): A path of the JSON event.
        """

        with open(json_schema, "r") as json_file:
            json_data = json.load(json_file)

        self.json_schema = json_data

    def _search_schema_recursively(self, search_dict, field):
        """
        Description
            Search a JSON schema recursively.
        Args
            search_dict (Dict): A JSON schema.
            field (String): A key to be searched in the JSON schema.
        Returns 
            fields_found (List): A list with the found objects.        
        """

        # A empty list to store the values
        fields_found = []

        # Compare the keys with the field passed and keep in the list
        for k, v in search_dict.items():
            if k == field:
                fields_found.append(v)

            # Check if the value of a key is a dict, and apply the function recursively
            elif isinstance(v, dict):
                results = self._search_schema_recursively(v, field)

                # Keep the values found in the list
                for result in results:
                    fields_found.append(result)

        return fields_found

    def _search_key_recursively(self, search_dict, field=None):
        """
        Description
            Search a JSON schema recursively.
        Args
            search_dict (Dict): A JSON schema.
            field (String): A key to be searched in the JSON schema.
        Returns 
            fields_found (List): The first item of the founds object list.
        """

        # If nothing is passed to the field params, then returns the json passed
        if field == None:
            return search_dict

        else:
            # A empty list to store the values
            fields_found = []

            # Compare the keys with the field passed and keep in the list
            for k, v in search_dict.items():
                if k == field:
                    fields_found.append(v)
                # Check if the value of a key is a dict, and apply the _search_schema_recursively function
                elif isinstance(v, dict):
                    results = self._search_schema_recursively(v, field)
                    for result in results:
                        fields_found.append(result)

            # Check the length of the list, is is 0 then the field is not in the json searched
            if len(fields_found) == 0:
                raise Exception(f"Error! The field {field} is not in the JSON SCHEMA")

            return fields_found[0]
    #TODO: Arrumar o nome da função
    def _ckeck_allfields(self, event, json_schema):
        """
        Description
            Check if all the keys of the event are in the JSON Schema.
        Args
            event (Dict): A JSON schema.
            json_schema (String): A path to the JSON Schema.
        Returns 
            Return a string or raise errors.        
        """

        # Iterate on the keys and values of the event
        for k, v in event.items():

            # Assign recursively the key "properties" to a variable
            json_properties = self._search_schema_recursively(json_schema, 'properties')[0]

            # Check if a value of the event is one of the tuple (int, float, str, bool)
            if not isinstance(v, (list, dict)):

                # Check if the key is not in json_properties
                if k not in json_properties.keys():
                    raise Exception(f"The field {k} is not in the JSON schema! {json_properties.keys()}")

            # Check if a value of the event is dict
            elif isinstance(v, dict):

                # Check if the key assigned to the dict value is in json_properties
                if k not in json_properties.keys():
                    raise Exception(f"The field {k} is not in the JSON schema! {json_properties.keys()}")

                # Apply the function recursively to access the nested layers
                self._ckeck_allfields(v, json_properties)

    def _check_required_fields(self, event, json_schema):
        """
        Description
            Check if all the required keys of the JSON Schema are in the event.
        Args
            event (Dict): A JSON schema.
            json_schema (String): A path to the JSON Schema.
        Returns 
            Returns none or raise descriptive errors.        
        """

        required_fields = []
        # Check the first layer
        for key in json_schema['required']:
            if key not in event.keys():
                required_fields.append(key)

        # Check the nested layers
        for item in json_schema['required']:
            value = self._search_schema_recursively(json_schema, item)[0]
            if value['type'] == 'object':
                for required_item in value['required']:
                    if required_item not in event[item].keys():
                        required_fields.append(required_item)
        # Raise a error if exists elements in the list
        if len(required_fields) > 0:
            raise Exception(f"The fields {required_fields} are required, check the JSON Schema!")

    def _recursion_check_type(self, json_dict):
        """
        Description
            Compare the types of each field in the event with the JSON schema.
        Args
            json_dict (Dict): A JSON event.
        Returns 
            Raise a error if the fields does not match.        
        """

        # Compare the type of the values, and keep only the ints,floats, strs and bools
        for k, v in json_dict.items():
            if isinstance(v, (str, int, bool, float)):

                # Search the value example of the key from the event in the JSON schema, and stores the type of it.
                value_type = type(self._search_schema_recursively(self.json_schema, k)[0]['examples'][0])

                # Compare the type of the value in the event with the JSON schema
                if (value_type != type(v)):
                    raise Exception(
                        f"Error! The type of the {k} field does not match the Schema. Should be {value_type}.")
            # If the value is a dict, so is applied the function recursively.
            elif isinstance(v, dict):
                self._recursion_check_type(v)

    def event_validation(self, event):
        """
        Description
            Check if the event JSON matchs with the JSON Schema
        Args
            json_dict (Dict): A JSON event.
        Returns 
            Return the event or raise a error if the fields does not match.        
        """

        # Check if the required fields of the JSON Schema are in the event
        self._check_required_fields(event, self.json_schema)

        # Check if the fields of a event are in the JSON Schema
        self._ckeck_allfields(event, self.json_schema)

        # Check if the types of the event's values matchs with the JSON Schema
        self._recursion_check_type(event)

        return event