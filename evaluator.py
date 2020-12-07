"""
# Problem 1: Garbled Circuit Evaluator (15 points)
"""

import circuit
import util
import json
from circuit import BooleanCircuit
from util import specialDecryption, specialEncryption
import codecs

decode_hex = codecs.getdecoder("hex_codec")

class GarbledCircuitEvaluator(BooleanCircuit):
    def __init__(self, from_json=None):
        # The superclass constructor initializes the gates and topological sorting
        super(GarbledCircuitEvaluator,self).__init__(from_json=from_json)

        # What remains is for us to load the garbling tables
        if from_json is not None:

            # Load the garbled tables
            gates = from_json["gates"]

            # TODO: your code goes here            
            for gid in gates:

                gate = gates[gid]

                self.gates[gid]["garble_table"] = gate["garble_table"]
            
    def convert_byte_array_to_hex_string(self, a):

        return ''.join('{:02x}'.format(x) for x in a)

    def garbled_evaluate(self, inp):
        # Precondition: initialized, topologically sorted
        #               has garbled tables
        #               inp is a mapping of wire labels for each input wire
        # Postcondition: self.wire_labels takes on labels resulting from this evaluation
        assert len(inp) == len(self.input_wires)
        self.wire_labels = {}

        # Set the wire labels for all the input wires
        for wid in self.input_wires:
            assert wid in inp, "Must provide a label for each wire"
            label = inp[wid]
            assert len(label) == 2 * 16  # Labels are keys, 16 bytes in hex
            self.wire_labels[wid] = label

        # TODO: Your code goes here
        for gid in self.sorted_gates:
            gate = self.gates[gid]
            a = self.wire_labels[gate["inp"][0]]
            b = self.wire_labels[gate["inp"][1]]

            c = None

            for entry in gate["garble_table"]:

                partial_decryption = specialDecryption(decode_hex(a)[0], decode_hex(entry)[0])

                if (partial_decryption != None):

                    complete_decryption = specialDecryption(decode_hex(b)[0], partial_decryption)

                    if (complete_decryption != None):

                        c = complete_decryption

                        break

            assert (c != None)

            self.wire_labels[gate["out"][0]] = self.convert_byte_array_to_hex_string(c)

        return dict((wid,self.wire_labels[wid]) for wid in self.output_wires)



if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("usage: python evaluator.py <circuit.json>")
        sys.exit(1)

    filename = sys.argv[1]
    obj = json.load(open(filename))

    # Circuit
    c = GarbledCircuitEvaluator(from_json=obj)
    print('Garbled circuit loaded: %d gates, %d input wires, %d output_wires, %d total' \
        % (len(c.gates), len(c.input_wires), len(c.output_wires), len(c.wires)), file=sys.stderr)

    # Evaluate the circuit
    inputs = obj["inputs"]
    json.dump(c.garbled_evaluate(inputs), sys.stdout, indent=4)
    print('') # end the line
