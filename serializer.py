"""
Theo Browne & Paul Revere
Distributed Systems and Algorithms 2016
Project 2
serializer.py
"""
# ==============================================================================

import base64

# ==============================================================================
#
class serializer(object):
    """
    Serialization/Deserialization for DS&A Project 1

    serialize( list(strings) )
    deserialize( string )
    """

    # ==========================================================================
    # serialize( list(strings) )
    # Takes list of strings and returns a base64 string of them packed together
    #   to be sent over tcp
    #
    @staticmethod
    def serialize(unpacked):
        serialized = []
        for data in unpacked:
            base64d_data = base64.b64encode(data)
            serialized.append(base64d_data)
        packed = '-'.join(serialized)
        return packed

    # ==========================================================================
    # deserialize( string )
    # Takes in a packed base64 string and turns it into a list of strings
    #
    @staticmethod
    def deserialize(packed):
        deserialized = []
        for base64d_data in packed.split('-'):
            data = base64.b64decode(base64d_data)
            deserialized.append(data)
        return deserialized

# ==============================================================================
#
if __name__ == "__main__":
    s1 = "String A"
    s2 = "String B"
    s3 = "String C"
    strings = [s1, s2, s3]
    print strings
    packed = serializer.serialize(strings)
    print packed
    unpacked = serializer.deserialize(packed)
    print unpacked
