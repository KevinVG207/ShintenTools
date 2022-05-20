class OBJ:
    def __init__(self, file_path):
        self.groups = parse_obj_to_groups(file_path)

class FileGroup:
    def __init__(self, name):
        self.name = name
        self.vertices = []
        self.uvs = []
        self.normals = []
        self.raw_faces = []
        self.faces = []
        self.other = []


def parse_obj_to_groups(file_path):
    vertices = []
    uvs = []
    normals = []
    unparsed = []
    groups = []
    mtllibs = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#'):
                continue
            elif line.startswith('mtllib '):
                mtllibs.append(line.split(' ', 1)[1])
            elif line.startswith('v '):
                vertices.append(line.split(' ')[1:])
            elif line.startswith('vt '):
                uvs.append(line.split(' ')[1:])
            elif line.startswith('vn '):
                normals.append(line.split(' ')[1:])
            else:
                unparsed.append(line)
        for line in unparsed:
            if line.startswith('g '):
                group_name = line.split(' ', 1)[1]
                groups.append(FileGroup(group_name))
                continue
            # TODO: Handle mtl texture
            elif line.startswith('usemtl '):
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
                groups[-1].raw_faces.append(face)
            else:
                groups[-1].other.append(line)
    for group in groups:
        print("=== " + group.name + " ===")
        print(group.raw_faces)

        vertices_conversion = {'': ''}
        uvs_conversion = {'': ''}
        normals_conversion = {'': ''}
        for i in range(len(group.raw_faces)):
            for j in range(len(group.raw_faces[i])):
                if group.raw_faces[i][j][0] not in vertices_conversion:
                    vertices_conversion[group.raw_faces[i][j][0]] = len(group.vertices)
                    group.vertices.append(vertices[group.raw_faces[i][j][0]])
                if len(group.raw_faces[i][j]) > 1:
                    if group.raw_faces[i][j][1] not in uvs_conversion:
                        uvs_conversion[group.raw_faces[i][j][1]] = len(group.uvs)
                        group.uvs.append(uvs[group.raw_faces[i][j][1]])
                if len(group.raw_faces[i][j]) > 2:
                    if group.raw_faces[i][j][2] not in normals_conversion:
                        normals_conversion[group.raw_faces[i][j][2]] = len(group.normals)
                        group.normals.append(normals[group.raw_faces[i][j][2]])
        print(group.vertices)
        print(group.uvs)
        print(group.normals)
        for i in range(len(group.raw_faces)):
            converted_face = []
            for j in range(len(group.raw_faces[i])):
                converted_indices = []
                converted_indices.append(vertices_conversion[group.raw_faces[i][j][0]])
                if len(group.raw_faces[i][j]) > 1:
                    converted_indices.append(uvs_conversion[group.raw_faces[i][j][1]])
                if len(group.raw_faces[i][j]) > 2:
                    converted_indices.append(normals_conversion[group.raw_faces[i][j][2]])
                converted_face.append(converted_indices)
            group.faces.append(converted_face)
        print(group.faces)
    return groups
                    