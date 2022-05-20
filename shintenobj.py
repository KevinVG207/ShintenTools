import argparse
import os
import objparser

SHINTEN_MATERIAL_EXTENSION = ".mat"

def main(args):
    args.raw_path = args.input_path[:-4]
    if not args.input_path.lower().endswith('.obj'):
        print('Not an obj file')
        return
    if not args.output_path:
        args.output_path = "Course"
    if not os.path.exists(args.input_path[:-4]+".mtl"):
        print("No mtl file found")
        return
    if not os.path.exists(args.raw_path + SHINTEN_MATERIAL_EXTENSION):
        print("No shinten material file found. Generate one with the argument -m")
        return
    
    # Load the obj file
    obj = objparser.OBJ(args.input_path)
    print("ok")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Creates Shinten Course models from a .obj file.")
    parser.add_argument("-i", "--input", dest="input_path", type=str, help="Input .obj file", required=True)
    parser.add_argument("-o", "--output", dest="output_path", type=str, help="Output .obj file", required=False)
    parser.add_argument("-m", "--material", dest="make_material_file", action='store_true', help="Generate a Shinten materials file.", required=False)
    parser.add_argument("-v", "--verbose", dest="verbose", action='store_true', help="Verbose output.", required=False)
    args = parser.parse_args()
    main(args)
