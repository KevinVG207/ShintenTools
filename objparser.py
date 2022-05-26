import os
import args
from PIL import Image


VERSION = '1.0'


class OBJ:
    version = VERSION

    def __init__(self, file_path):
        self.coord_bounds = [None] * 6
        self.groups = parse_obj_to_groups(file_path, self.coord_bounds)
    
    def write_files(self, output_path):
        for group_name, group in self.groups.items():
            print(f"Writing material group: {group_name}")
            for part in group.values():
                part.write_file(output_path)
    
    def write_material_file(self, output_path):
        print(f"Writing material file: {output_path}")
        existing_materials = []
        out_lines = []
        append = os.path.exists(output_path)
        if append:
            with open(output_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith("# STTools Material: "):
                        existing_materials.append(line.split(': ', 1)[1].strip())

        for parts_groups in self.groups.values():
            first = True
            part_lines = []
            for part in parts_groups.values():
                if not append or (append and part.material not in existing_materials):
                    if first:
                        first = False
                        part_lines.append(f"# STTools Material: {part.material}")
                        if args.args.enable_colmeshes:
                            part_lines.append(part.get_colmesh_string())
                        else:
                            part_lines.append(part.generate_unity_material())
                    else:
                        part_lines.append(part.get_copy_string())
                    
            if part_lines:
                out_lines.append("\n".join(part_lines))

        if append:
            with open(output_path, 'a', encoding='utf-8') as f:
                if out_lines:
                    f.write('\n\n')
                    f.write('\n\n'.join(out_lines))
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("# Materials generated by Shinten Tools\nClear\n\n")
                f.write('\n\n'.join(out_lines))
                if args.args.enable_colmeshes and not args.args.no_oob:
                    f.write('\n\n')
                    f.write(make_out_of_bounds_triggers(self.coord_bounds))


class MaterialGroup:
    version = VERSION

    def __init__(self, material):
        self.material = material
        self.texture = None
        self.vertices = []
        self.uvs = []
        self.normals = []
        self.raw_faces = []
        self.faces = []
        self.other = []
    
    def __str__(self):
        header = [
            f"# OBJ Generated by ShintenTools",
            f"# Version: {self.version}",
            f"# Material: {self.material}"
        ]

        elements = [
            '\n'.join(header),
            coords_string(self.vertices, 'v'),
            coords_string(self.uvs, 'vt'),
            coords_string(self.normals, 'vn'),
            faces_string(self.faces)
        ]
        if self.other:
            elements.insert(1, '\n'.join(self.other))

        return '\n'.join(elements)
    
    def write_file(self, output_path):
        if args.args.verbose:
            print(f"Writing {self.material} to {output_path}")
        file_path = os.path.join(output_path, self.material + '.obj')
        with open(file_path, "w", encoding='utf-8') as file:
            file.write(str(self))
    
    def generate_unity_material(self):
        shader = "'Legacy Shaders/Bumped Diffuse'"

        if self.texture and os.path.isfile(os.path.join(args.args.input_folder, self.texture)):
            img = Image.open(os.path.join(args.args.input_folder, self.texture))
            if has_transparency(img):
                shader = "'Legacy Shaders/Transparent/Cutout/Diffuse'"
            img.close()

        lines = [
            "New",
            f"Mesh \'{os.path.join(args.args.output_folder_relative, self.material)}.obj\'",
            f"BIShader {shader}",
            f"Texture _MainTex \'{self.texture}\'",
            "MaterialPropertyFloat _Metallic 0.3",
            "MaterialPropertyFloat _Glossiness 0.1"
        ]
        return '\n'.join(lines)

    def get_copy_string(self):
        return f"Copy;Mesh \'{os.path.join(args.args.output_folder_relative, self.material)}.obj\'"
    
    def get_colmesh_string(self):
        return f"New\nColMesh \'{os.path.join(args.args.output_folder_relative, self.material)}.obj\'"

def center(coords):
    return (coords[0] + coords[1]) / 2


def dist(coords):
    return coords[1] - coords[0]


def make_out_of_bounds_triggers(coord_bounds):
    return '\n'.join([
        f"Clear;New;ColBox {-coord_bounds[0] + 100} {center(coord_bounds[2:4])} {center(coord_bounds[4:6])} {100} {dist(coord_bounds[2:4])} {dist(coord_bounds[4:6])};Death",
        f"Clear;New;ColBox {-coord_bounds[1] - 100} {center(coord_bounds[2:4])} {center(coord_bounds[4:6])} {100} {dist(coord_bounds[2:4])} {dist(coord_bounds[4:6])};Death",
        f"Clear;New;ColBox {-center(coord_bounds[0:2])} {coord_bounds[2] - 100} {center(coord_bounds[4:6])} {dist(coord_bounds[0:2])} {100} {dist(coord_bounds[4:6])};Death",
        f"Clear;New;ColBox {-center(coord_bounds[0:2])} {coord_bounds[3] + 100} {center(coord_bounds[4:6])} {dist(coord_bounds[0:2])} {100} {dist(coord_bounds[4:6])};Death",
        f"Clear;New;ColBox {-center(coord_bounds[0:2])} {center(coord_bounds[2:4])} {coord_bounds[4] - 100} {dist(coord_bounds[0:2])} {dist(coord_bounds[2:4])} {100};Death",
        f"Clear;New;ColBox {-center(coord_bounds[0:2])} {center(coord_bounds[2:4])} {coord_bounds[5] + 100} {dist(coord_bounds[0:2])} {dist(coord_bounds[2:4])} {100};Death"
    ])


def has_transparency(img):
    # Transparency check taken from:
    # https://stackoverflow.com/questions/43864101/python-pil-check-if-image-is-transparent
    if img.info.get("transparency", None) is not None:
        return True
    if img.mode == "P":
        transparent = img.info.get("transparency", -1)
        for _, index in img.getcolors():
            if index == transparent:
                return True
    elif img.mode == "RGBA":
        extrema = img.getextrema()
        if extrema[3][0] < 255:
            return True
    return False


def coords_string(coords, type):
    return '\n'.join([type + ' ' + ' '.join([str(coord) for coord in coord_group]) for coord_group in coords])
    

def faces_string(faces):
    out = []
    current_smooth = None
    for face in faces:
        if face['smoothing'] != current_smooth:
            current_smooth = face['smoothing']
            out.append(f"s {current_smooth}")
        cur_face = []
        for indices in face['indices']:
            cur_indices = []
            for index in indices:
                if isinstance(index, str):
                    cur_indices.append(index)
                else:
                    cur_indices.append(str(index + 1))
            cur_face.append('/'.join(cur_indices))
        out.append('f ' + ' '.join(cur_face))
        # out.append('f ' + ' '.join(['/'.join([str(index + 1) for index in indices]) for indices in face['indices']]))

    return '\n'.join(out)


def create_subgroup(raw_subset_faces, vertices, uvs, normals):
    subset_vertices = []
    subset_uvs = []
    subset_normals = []
    subset_faces = []
    vertices_conversion = {'': ''}
    uvs_conversion = {'': ''}
    normals_conversion = {'': ''}
    for i in range(len(raw_subset_faces)):
        for j in range(len(raw_subset_faces[i]['indices'])):
            if raw_subset_faces[i]['indices'][j][0] not in vertices_conversion:
                vertices_conversion[raw_subset_faces[i]['indices'][j][0]] = len(subset_vertices)
                subset_vertices.append(vertices[raw_subset_faces[i]['indices'][j][0]])
            if len(raw_subset_faces[i]['indices'][j]) > 1:
                if raw_subset_faces[i]['indices'][j][1] not in uvs_conversion:
                    uvs_conversion[raw_subset_faces[i]['indices'][j][1]] = len(subset_uvs)
                    subset_uvs.append(uvs[raw_subset_faces[i]['indices'][j][1]])
            if len(raw_subset_faces[i]['indices'][j]) > 2:
                if raw_subset_faces[i]['indices'][j][2] not in normals_conversion:
                    normals_conversion[raw_subset_faces[i]['indices'][j][2]] = len(subset_normals)
                    subset_normals.append(normals[raw_subset_faces[i]['indices'][j][2]])
    
    for i in range(len(raw_subset_faces)):
        converted_face = []
        for j in range(len(raw_subset_faces[i]['indices'])):
            converted_indices = []
            converted_indices.append(vertices_conversion[raw_subset_faces[i]['indices'][j][0]])
            if len(raw_subset_faces[i]['indices'][j]) > 1:
                converted_indices.append(uvs_conversion[raw_subset_faces[i]['indices'][j][1]])
            if len(raw_subset_faces[i]['indices'][j]) > 2:
                converted_indices.append(normals_conversion[raw_subset_faces[i]['indices'][j][2]])
            converted_face.append(converted_indices)
        subset_faces.append({'indices': converted_face, 'smoothing': raw_subset_faces[i]['smoothing']})
    return subset_vertices, subset_uvs, subset_normals, subset_faces


def parse_obj_to_groups(file_path, coord_bounds):
    print("Parsing OBJ file...")
    vertices = []
    uvs = []
    normals = []
    unparsed = []
    groups = {}
    mtllibs = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('mtllib '):
                mtllibs.append(line.split(' ', 1)[1])
            elif line.startswith('v '):
                coords = line.split(' ')[1:]
                for i in range(len(coords)):
                    cur_coord = float(coords[i])
                    if not coord_bounds[i * 2]:
                        coord_bounds[i * 2] = cur_coord
                        coord_bounds[i * 2 + 1] = cur_coord
                    else:
                        if cur_coord < coord_bounds[i * 2]:
                            coord_bounds[i * 2] = cur_coord
                        if cur_coord > coord_bounds[i * 2 + 1]:
                            coord_bounds[i * 2 + 1] = cur_coord
                vertices.append(coords)
            elif line.startswith('vt '):
                uvs.append(line.split(' ')[1:])
            elif line.startswith('vn '):
                normals.append(line.split(' ')[1:])
            else:
                unparsed.append(line)
        current_group = None
        current_smooth = "off"
        for line in unparsed:
            if line.startswith('usemtl '):
                material = line.split(' ', 1)[1]
                if material not in groups:
                    groups[material] = MaterialGroup(material)
                current_group = material
                continue
            elif line.startswith('s '):
                current_smooth = line.split(' ', 1)[1]
                continue
            elif line.startswith('f '):
                face = line.split(' ')[1:]
                for i in range(len(face)):
                    face[i] = face[i].split('/')
                    face[i][0] = int(face[i][0]) - 1
                    if len(face[i]) > 1:
                        if face[i][1] != '':
                            face[i][1] = int(face[i][1]) - 1
                    if len(face[i]) > 2:
                        face[i][2] = int(face[i][2]) - 1
                groups[current_group].raw_faces.append({'indices': face, 'smoothing': current_smooth})
            else:
                continue
    
    
    for mtllib in mtllibs:
        mtl_path = os.path.join(os.path.dirname(file_path), mtllib)
        if not os.path.exists(mtl_path):
            print(f"Could not find material library '{mtl_path}'")
            quit()
        with open(mtl_path, 'r', encoding='utf-8') as f:
            cur_material = None
            for line in f:
                if line.startswith('newmtl '):
                    cur_material = line.strip().split(' ', 1)[1]
                if line.startswith('map_Kd '):
                    texture_file = line.strip().split(' ', 1)[1]
                    if "\\" in texture_file:
                        texture_file = texture_file.split("\\")[-1]
                    if "/" in texture_file:
                        texture_file = texture_file.split("/")[-1]
                    groups[cur_material].texture = os.path.join(args.args.texture_path, texture_file)
    
    print("Grouping materials...")
    for group in groups.values():
        print("=== " + group.material + " ===")
        if args.args.verbose:
            print(group.raw_faces)

        group.vertices, group.uvs, group.normals, group.faces = create_subgroup(group.raw_faces, vertices, uvs, normals)
        
        if args.args.verbose:
            print(group.vertices)
            print(group.uvs)
            print(group.normals)
            print(group.faces)
    
    print("Truncating meshes...")
    truncated_groups = {}
    part = 0
    while len(groups) > 0:
        cur_key = list(groups.keys())[0]
        print(f"=== {cur_key} ===")
        cur_group = groups[cur_key]
        truncated_groups[cur_key] = {}
        part = 1
        while True:
            stop_splitting = False
            new_group_material = cur_group.material + f"_part{part}" if part > 1 else cur_group.material

            if args.args.verbose:
                print(f"Part {part}")

            new_group = MaterialGroup(new_group_material)
            new_group.texture = cur_group.texture
            cur_vertices = set()
            cur_faces = []
            while len(cur_group.faces) > 0 and not stop_splitting:
                cur_face = cur_group.faces.pop(0)
                for indices in cur_face['indices']:
                    if tuple(indices) not in cur_vertices:
                        if len(cur_vertices) == 65535:
                            stop_splitting = True
                            cur_group.faces.insert(0, cur_face)
                            break
                        cur_vertices.add(tuple(indices))
                if not stop_splitting:
                    cur_faces.append(cur_face)
            if args.args.verbose:
                print(f"Part vertex count: {len(cur_vertices)}")
                print(f"Making new subgroup {new_group.material}")
            new_group.vertices, new_group.uvs, new_group.normals, new_group.faces = create_subgroup(cur_faces, cur_group.vertices, cur_group.uvs, cur_group.normals)
            truncated_groups[cur_key][new_group_material] = new_group
            if len(cur_group.faces) == 0:
                groups.pop(cur_key)
                break
            part += 1
    
    return truncated_groups
