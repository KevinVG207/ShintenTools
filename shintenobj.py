import argparse
import os
import objparser
import args
import time

SHINTEN_MATERIAL_EXTENSION = ".mat"

def main():
    args.args.raw_path = args.args.input_path[:-4]
    if not args.args.input_path.lower().endswith('.obj'):
        print('Not an obj file')
        return
    if not os.path.exists(args.args.input_path):
        print('Input file does not exist')
        return
    args.args.input_folder = os.path.dirname(args.args.input_path)
    if not args.args.output_folder_relative:
        args.args.output_folder = os.path.dirname(args.args.input_path)
    else:
        args.args.output_folder = os.path.join(os.path.dirname(args.args.input_path), args.args.output_folder_relative)
    if args.args.material_file and not os.path.exists(args.args.material_file):
        print("Provided material file not found.")
        return
    if not args.args.material_file:
        args.args.material_file = args.args.raw_path + SHINTEN_MATERIAL_EXTENSION
    if not os.path.isdir(args.args.output_folder):
        os.makedirs(args.args.output_folder)
    
    time_before = time.time()
    # Load the obj file
    obj = objparser.OBJ(args.args.input_path)
    obj.write_material_file(args.args.material_file)
    obj.write_files(args.args.output_folder)
    time_after = time.time()
    print("Finished in {:.2f} seconds".format(time_after - time_before))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Creates Shinten Course models from a .obj file.")
    parser.add_argument("-i", "--input", dest="input_path", type=str, help="Input .obj file", required=True)
    parser.add_argument("-o", "--output", dest="output_folder_relative", type=str, help="Output folder (otherwise files will be written in the folder of the input. Relative to input file's location.)", required=False)
    parser.add_argument("-m", "--material", dest="material_file", action='store_true', help="Manually provide a Shinten Tools-generated materials file.", required=False)
    parser.add_argument("-t", "--texture", dest="texture_path", type=str, help="Path to the texture folder that will be used in the materials file. (Relative to input file's location.)", required=False)
    parser.add_argument("-c", "--colmesh", dest="enable_colmeshes", action='store_true', help="Write all materials with collision meshes.", required=False)
    parser.add_argument("-v", "--verbose", dest="verbose", action='store_true', help="Verbose output.", required=False)
    parser.add_argument("-no-oob", dest="no_oob", action='store_true', help="Don't automatically add out of bounds triggers around your track.", required=False)
    args.args = parser.parse_args()
    main()
