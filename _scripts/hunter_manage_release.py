#!/usr/bin/env python3

# You will need to install "hub"
# (a github command line client : https://github.com/github/hub)

import sys
import os
import subprocess
import urllib.request
import hashlib
import typing
import shutil


# Predefined types for clarity
ReleaseName = typing.NewType("ReleaseName", str)
TargetBranch = typing.NewType("TargetBranch", str)
Toolchain = typing.NewType("Toolchain", str)
HunterProjectName = typing.NewType("HunterProjectName", str)
Sha1String = typing.NewType("Sha1String", str)
Url = typing.NewType("Url", str)
GitUrl = typing.NewType("GitUrl", str)
Filename = typing.NewType("Filename", str)
Folder = typing.NewType("Folder", str)
Command = typing.NewType("Command", str)
CmakeCode = typing.NewType("CmakeCode", str)

THISDIR = os.path.dirname(os.path.realpath(__file__)) + "/"
MAIN_REPO = os.path.realpath( THISDIR + "/../") + "/"
HUNTER_REPO = os.path.realpath( MAIN_REPO + "/hunter/") + "/"


def hunter_cmake_file(project: HunterProjectName) -> Filename:
  result = "{0}/cmake/projects/{1}/hunter.cmake".format(HUNTER_REPO, project)
  return result


def hunter_edit_hunter_cmake(
  hunter_project_name: HunterProjectName,
  cmake_code : CmakeCode
  ):
  cmake_file = HUNTER_REPO + "/cmake/projects/" + hunter_project_name + "/hunter.cmake"
  with open(cmake_file, "r") as f:
    lines = f.readlines()
  output = ""
  for line in lines:
    if "hunter_add_version(" in line:
      output = output + "\n" + cmake_code + "\n"
    output = output + line
  with open(cmake_file, "w") as f:
    f.write(output)
    print("""
    File {} was edited, with this addition
    ------------------------------
    {}
    ------------------------------
    """.format(cmake_file, cmake_code))


def hunter_edit_default_version(
  hunter_project_name: HunterProjectName,
  release_name : ReleaseName
  ):
  cmake_file = HUNTER_REPO + "cmake/configs/default.cmake"
  with open(cmake_file, "r") as f:
    lines = f.readlines()

  what_to_search = "hunter_default_version(" + hunter_project_name
  what_to_write = "hunter_default_version({} VERSION {})\n".format(hunter_project_name, release_name)
  found = False
  output = ""
  for line in lines:
    if what_to_search in line:
      line = what_to_write
      found = True
    output = output + line
  if found:
    with open(cmake_file, "w") as f:
      f.write(output)
    print("Wrote:     {}in:        {}".format(what_to_write, cmake_file))
  return found


def _hunter_add_version_code(
  hunter_project_name: HunterProjectName,
  release_name: ReleaseName,
  url: Url,
  sha1: Sha1String
  ) -> (Filename, CmakeCode):
  cmake_version_code = """
hunter_add_version(
    PACKAGE_NAME
    __HunterProjectName__
    VERSION
    __ReleaseName__
    URL
    "__Url__"
    SHA1
    __Sha1__
)
  """
  cmake_version_code = cmake_version_code.replace("__HunterProjectName__", hunter_project_name)
  cmake_version_code = cmake_version_code.replace("__ReleaseName__", release_name)
  cmake_version_code = cmake_version_code.replace("__Url__", url)
  cmake_version_code = cmake_version_code.replace("__Sha1__", sha1)
  return( hunter_cmake_file(hunter_project_name), cmake_version_code )


def sha1sum(filename: Filename) -> Sha1String:
    h = hashlib.sha1()
    with open(filename, 'rb', buffering=0) as f:
        for b in iter(lambda : f.read(128*1024), b''):
            h.update(b)
    return h.hexdigest()


def my_run_command(cmd: Command, cwd: Folder):
  print("Run command: {0} (in folder {1})".format(cmd, cwd))
  subprocess.run(cmd, cwd = cwd, check=True, shell=True)


def github_url_to_url(git_url: GitUrl) -> Url:
  result = git_url.replace("git@github.com:", "https://github.com/")
  result = result.replace(".git", "")
  return result


def get_project_push_url(project: HunterProjectName) -> GitUrl:
  print("get_project_push_url({})".format(project))
  repo_folder = MAIN_REPO + project
  result = subprocess.run("git remote show origin", shell=True, cwd=repo_folder, capture_output=True)
  out = result.stdout.decode("utf-8")
  out_lines = out.split("\n")
  for line in out_lines:
    if "Push  URL:" in line:
      result = line.replace("Push  URL:", "").strip()
  return result


def get_project_github_url(project):
  return github_url_to_url( get_project_push_url(project) )


def _project_create_release_do_release(
        hunter_project_name : HunterProjectName,
        release_name: ReleaseName,
        target_branch: TargetBranch
        ) -> (Url, Sha1String):
  repo_folder = MAIN_REPO + "/" + hunter_project_name
  cmd = "hub release create -t {0} -m \"{1}\" {1}".format(target_branch, release_name)
  my_run_command(cmd, repo_folder)

  release_url = get_project_github_url(hunter_project_name) + "/archive/" + release_name + ".tar.gz"
  print("Created release " + release_url)
  tmp_file = "tmp.tgz"
  print("Downloading release to get its sha1 : {}".format(release_url))
  urllib.request.urlretrieve(release_url, "tmp.tgz")
  sha1 = sha1sum(tmp_file)
  os.remove(tmp_file)
  return (release_url, sha1)


def project_create_release(
        hunter_project_name : HunterProjectName,
        release_name: ReleaseName,
        target_branch: TargetBranch
        ) -> (Url, Sha1String):
  release_url, sha1 = _project_create_release_do_release(
    hunter_project_name=hunter_project_name,
    release_name=release_name,
    target_branch=target_branch
  )

  hunter_cmake_filename, cmake_code = _hunter_add_version_code(
    hunter_project_name = hunter_project_name,
    release_name = release_name,
    url= release_url,
    sha1 = sha1
  )

  print("In order to add this release to hunter ")
  print("Edit the file : {}".format(hunter_cmake_filename))
  print("And add this code : \n{}".format(cmake_code))
  anwser = input("Shall I edit this file (yes/no)")
  if anwser == "yes":
    hunter_edit_hunter_cmake(hunter_project_name, cmake_code)

  print("In order to set this version as default")
  default_cmake_file = HUNTER_REPO + "cmake/configs/default.cmake"
  print("You need to edit the file : {}".format(default_cmake_file))
  anwser = input("Shall I edit this file (yes/no)")
  if anwser == "yes":
    hunter_edit_default_version(hunter_project_name, release_name)
  return True


def project_delete_release(hunter_project_name: HunterProjectName, release_name: ReleaseName):
  repo_folder = MAIN_REPO + "/" + hunter_project_name
  cmd = "hub release delete {0}".format(release_name)
  my_run_command(cmd, repo_folder)


def test_build(app_folder: Folder, clean):
  app_folder = MAIN_REPO + app_folder
  build_folder = app_folder + "/build"
  if clean:
    if os.path.isdir(build_folder):
      shutil.rmtree(build_folder)
  if not os.path.isdir(build_folder):
    os.mkdir(build_folder)
  my_run_command("cmake .. -GNinja -DHUNTER_ENABLED=ON", build_folder)
  my_run_command("ninja", build_folder)

def add_polly_path():
  polly_bin_path = ":{}polly/bin".format(MAIN_REPO)
  os.environ["PATH"] = os.environ["PATH"] + ":" + polly_bin_path


def polly_help():
  add_polly_path()
  my_run_command("polly.py --help", HUNTER_REPO)


def hunter_test_build(hunter_project_name: HunterProjectName, toolchain: Toolchain):
  add_polly_path()
  cmd = "TOOLCHAIN={} PROJECT_DIR=examples/{} ./jenkins.py".format(toolchain, hunter_project_name)
  my_run_command(cmd, HUNTER_REPO)




def help():
  help_str = """
Usage:
{0} project_create_release HunterProjectName TargetBranch ReleaseName
{0} project_delete_release HunterProjectName ReleaseName
{0} test_build app_folder [clean]
{0} hunter_test_build HunterProjectName Toolchain
{0} hunter_list_toolchains
""".format(sys.argv[0])
  print(help_str)




def main():
  if len(sys.argv) == 1 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
    help()
    sys.exit(1)

  command = sys.argv[1]
  if command == "project_create_release":
    hunter_project_name = sys.argv[2]
    target_branch = sys.argv[3]
    release_name = sys.argv[4]
    result = project_create_release(
      hunter_project_name = hunter_project_name,
      target_branch = target_branch,
      release_name = release_name)
    print(result)
  elif command == "project_delete_release":
    hunter_project_name = sys.argv[2]
    release_name = sys.argv[3]
    project_delete_release(hunter_project_name, release_name)
  elif command == "test_build":
    app_folder = sys.argv[2]
    clean = False
    if len(sys.argv) > 3 and sys.argv[3] == "clean":
      clean = True
    test_build(app_folder, clean)
  elif command == "hunter_test_build":
    hunter_project_name = sys.argv[2]
    toolchain = sys.argv[3]
    hunter_test_build(hunter_project_name, toolchain)
  elif command == "hunter_list_toolchains":
    polly_help()
  else:
    help()


if __name__ == "__main__":
  main()
