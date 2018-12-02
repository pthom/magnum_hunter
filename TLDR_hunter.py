#!/usr/bin/env python3

# This script tries to simplify most of the manual actions described in
# https://docs.hunter.sh/en/latest/creating-new/create/cmake.html

# You will need to install "hub"
# (a github command line client : https://github.com/github/hub)
# You will also need to instal click : pip3 install click

import sys
import os
import subprocess
import urllib.request
import hashlib
import typing
import shutil
import click
import webbrowser


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

THISDIR = os.path.dirname(os.path.realpath(__file__)) + os.sep
MAIN_REPO = THISDIR
HUNTER_REPO = os.path.realpath( MAIN_REPO + "/hunter/") + os.sep


@click.group()
def cli():
  """
  This script tries to simplify most of the manual actions described in
  https://docs.hunter.sh/en/latest/creating-new/create/cmake.html

  \b
  Info about hunter branching model:
    * branch test.project_name = this branch contains all the modifications
      (packages and version + appveyor/travis CI scripts)
      This branch can be pushed to your own fork of hunter, so that you can test
      the build through Appveyor and Travis.
      This is the branch where you work & do your commits, and where you can test the CI
    * branch pr.project_name = pull request candidate for hunter repo
            (https://github.com/ruslo/hunter)
            This is the same aa the branch test.project_name except for the
            files appveyor.yml and .travis.yml.
    * branch pr.pkg.project_name = pull request candidate for hunter package testing templates
            (https://github.com/ingenue/hunter)
            this branch shall contains only modifications to appveyor.yml and .travis.yml
  """
  pass


def _hunter_cmake_file(project: HunterProjectName) -> Filename:
  result = "{0}/cmake/projects/{1}/hunter.cmake".format(HUNTER_REPO, project)
  return result


def _hunter_edit_hunter_cmake(
  hunter_project_name: HunterProjectName,
  cmake_code : CmakeCode
  ):
  cmake_file = HUNTER_REPO + "/cmake/projects/" + hunter_project_name + "/hunter.cmake"
  with open(cmake_file, "r") as f:
    lines = f.readlines()
  output = ""
  done = False
  for line in lines:
    if "hunter_add_version(" in line and done == False:
      output = output + "\n" + cmake_code + "\n"
      done = True
    output = output + line
  with open(cmake_file, "w") as f:
    f.write(output)
    print("""
    File {} was edited, with this addition
    ------------------------------
    {}
    ------------------------------
    """.format(cmake_file, cmake_code))


def _hunter_edit_default_version(
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
  return( _hunter_cmake_file(hunter_project_name), cmake_version_code )


def _sha1sum(filename: Filename) -> Sha1String:
    h = hashlib.sha1()
    with open(filename, 'rb', buffering=0) as f:
        for b in iter(lambda : f.read(128*1024), b''):
            h.update(b)
    return h.hexdigest()


def _my_run_command(cmd: Command, cwd: Folder):
  print("Run command: {0} (in folder {1})".format(cmd, cwd))
  subprocess.run(cmd, cwd = cwd, check=True, shell=True)


def _my_run_command_get_output(cmd: Command, cwd: Folder):
  result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True)
  out = result.stdout.decode("utf-8")
  return out


def _github_url_to_url(git_url: GitUrl) -> Url:
  result = git_url.replace("git@github.com:", "https://github.com/")
  result = result.replace(".git", "")
  return result


def _get_project_push_url(project: HunterProjectName) -> GitUrl:
  print("get_project_push_url({})".format(project))
  repo_folder = MAIN_REPO + project
  out = _my_run_command_get_output("git remote show origin", cwd=repo_folder)
  out_lines = out.split("\n")
  for line in out_lines:
    if "Push  URL:" in line:
      result = line.replace("Push  URL:", "").strip()
  return result


def _get_project_github_url(project):
  return _github_url_to_url( _get_project_push_url(project) )


def _project_create_release_do_release(
        hunter_project_name : HunterProjectName,
        release_name: ReleaseName,
        target_branch: TargetBranch
        ) -> (Url, Sha1String):
  repo_folder = MAIN_REPO + "/" + hunter_project_name
  cmd = "hub release create -t {0} -m \"{1}\" {1}".format(target_branch, release_name)
  _my_run_command(cmd, repo_folder)

  release_url = _get_project_github_url(hunter_project_name) + "/archive/" + release_name + ".tar.gz"
  print("Created release " + release_url)
  tmp_file = "tmp.tgz"
  print("Downloading release to get its sha1 : {}".format(release_url))
  urllib.request.urlretrieve(release_url, "tmp.tgz")
  sha1 = _sha1sum(tmp_file)
  os.remove(tmp_file)
  return (release_url, sha1)

@cli.command()
@click.argument("project_name", required=True)
@click.argument("target_branch", required=True)
@click.argument("release_name", required=True)
def project_create_release(
        project_name : HunterProjectName,
        target_branch: TargetBranch,
        release_name: ReleaseName
        ):
  """
  Creates a release on github for a project and optionally publish it to hunter

  \b
  Steps:
  * Creates a github release for a project (which must be subfolder of this repo)
  * Compute the sha1 of this release
  * Optionally add this release to hunter/cmake/project/project_name/hunter.cmake
  * Optionally make this release default in hunter/cmake/configs/defaults.cmake
  """
  release_url, sha1 = _project_create_release_do_release(
    hunter_project_name=project_name,
    release_name=release_name,
    target_branch=target_branch
  )

  hunter_cmake_filename, cmake_code = _hunter_add_version_code(
    hunter_project_name = project_name,
    release_name = release_name,
    url= release_url,
    sha1 = sha1
  )

  print("In order to add this release to hunter ")
  print("Edit the file : {}".format(hunter_cmake_filename))
  print("And add this code : \n{}".format(cmake_code))
  anwser = input("Shall I edit this file (yes/no)")
  if anwser == "yes":
    _hunter_edit_hunter_cmake(project_name, cmake_code)

  print("In order to set this version as default")
  default_cmake_file = HUNTER_REPO + "cmake/configs/default.cmake"
  print("You need to edit the file : {}".format(default_cmake_file))
  anwser = input("Shall I edit this file (yes/no)")
  if anwser == "yes":
    _hunter_edit_default_version(project_name, release_name)



@cli.command()
@click.argument("project_name", required=True)
@click.argument("release_name", required=True)
def project_delete_release(project_name: HunterProjectName, release_name: ReleaseName):
  """
  Delete a release from github for a project (a subfolder here)
  """
  repo_folder = MAIN_REPO + "/" + project_name
  cmd = "hub release delete {0}".format(release_name)
  _my_run_command(cmd, repo_folder)


def _is_windows():
  return os.name == "Windows" or os.name == "nt"


@cli.command()
@click.argument("project_name", required=True)
@click.argument("toolchain", default="default")
@click.option("--clean/--no-clean", default = False)
def test_build(project_name: Folder, toolchain: Toolchain, clean):
  """
  \b
  Helps to build a project using hunter.

  The project must be a subfolder of this repo).
  Basically it does this:

  \b
  export PATH=$(pwd)/polly/bin:$PATH
  mkdir build.project_name
  cd build.project_name
  polly.py --home --toolchain toolchain  # polly.py is a building script provided by polly

  \b
  Notes:
  * polly.py selects automatically the correct cmake generator according to the toolchain
  * Use `hunter-list-toolchains --filter` in order to find the available toolchains
  * if you want to use the toolchains manually, do:
  > cmake your/src/folder -DCMAKE_TOOLCHAIN_FILE=path/to/polly/toolchain.cmake
  """
  _add_polly_path()
  project_folder = MAIN_REPO + project_name
  build_folder = "{}/build.{}".format(MAIN_REPO, project_name)
  if clean:
    if os.path.isdir(build_folder):
      shutil.rmtree(build_folder)
  if not os.path.isdir(build_folder):
    os.mkdir(build_folder)
  _my_run_command(
    "polly.py --home {} --toolchain {}".format(project_folder, toolchain),
    build_folder)


def _has_python3_exe():
  try:
    _my_run_command("which python3", MAIN_REPO)
  except:
    return False
  return True

def python3_exe():
  if _has_python3_exe():
    python3_exe = "python3"
  else:
    python3_exe = "python"
  return python3_exe


def _add_polly_path():
  polly_bin_path = "{}polly".format(MAIN_REPO) + os.sep + "bin"
  os.environ["PATH"] = os.environ["PATH"] + os.pathsep + polly_bin_path
  print(os.environ["PATH"])


@cli.command()
@click.option("--filter", default = "")
def hunter_list_toolchains(filter: str):
  """
  Lists hunter toolchains (polly.py --help)
  """
  _add_polly_path()
  if _is_windows():
    out = _my_run_command_get_output("polly.bat --help", HUNTER_REPO)
  else:
    out = _my_run_command_get_output("polly.py --help", HUNTER_REPO)
  lines = out.split("\n")
  toolchains = []
  start = False
  for line in lines:
    if "optional arguments" in line:
      break
    if start == True and len(line.strip())> 0:
      toolchains.append(line.strip())
    if "Available toolchains" in line:
      start = True
  result = ""
  filtered_toolchains = [ t for t  in toolchains if filter in t ]
  result = "\n".join(filtered_toolchains)
  print(result)


def _is_git_repo_clean(folder: Folder) -> bool:
  out = _my_run_command_get_output("git status", cwd=folder)
  lines = out.split("\n")
  is_clean = any( [ "working tree clean" in line for line in lines] )
  return is_clean


def _git_branch(folder: Folder) -> str:
  out = _my_run_command_get_output("git branch", cwd=folder)
  lines = out.split("\n")
  def is_current_branch(branch_name):
    return len(branch_name) > 0 and branch_name[0] == '*'
  current_branches = filter(is_current_branch, lines)
  current_branch = list(current_branches)[0].replace("* ", "")
  return current_branch


def _cmake_code_use_hunter_release(url: Url, sha1: Sha1String) -> CmakeCode:
  code = """
  HunterGate(
    URL "__url__"
    SHA1 "__sha1__"
  )
  """
  code = code.replace("__url__", url)
  code = code.replace("__sha1__", sha1)
  return code


@cli.command()
@click.argument("release_name", required=True)
def hunter_delete_release(release_name: ReleaseName):
  """
  Deletes a hunter release on github
  """
  repo_folder = HUNTER_REPO
  cmd = "hub release delete {0}".format(release_name)
  _my_run_command(cmd, repo_folder)


@cli.command()
@click.argument("release_name", required=True)
def hunter_create_release(release_name: ReleaseName):
  """
  Publish a release on your hunter fork and assist you to use this hunter release in a sample app
  """
  answer = input("Create hunter release on github ? Type y to confirm: ")
  if answer != "y":
    print("abort")
    return False

  test_branch = _git_branch(HUNTER_REPO)
  if not test_branch.find("test.") == 0:
    print("Your hunter repo should be on a test.[project_name] branch : abort")
    return False
  project_name = test_branch.split(".")[1]
  pr_branch = "pr." + project_name
  print("project_name = " + project_name)
  print("test_branch = " + test_branch)
  print("pr_branch = " + pr_branch)

  release_url, sha1 = _project_create_release_do_release(
    hunter_project_name="hunter",
    release_name=release_name,
    target_branch=pr_branch
  )
  print("Release url:" + release_url)
  print("sha1:" + sha1)
  cmake_code  = _cmake_code_use_hunter_release(release_url, sha1)
  print("Here is the code in order to use this release:")
  print("**********************************************")
  print(cmake_code)
  print("**********************************************")
  dst_file = "magnum_example_app/CMakeLists.txt"
  print("put is inside {}".format(dst_file))



@cli.command()
@click.argument("project_name", required=True)
@click.argument("toolchain", required=True)
def hunter_test_build(project_name: HunterProjectName, toolchain: Toolchain):
  """
  Builds a project inside hunter using the given toolchain

  \b
  Basically it does this :
    > export PATH=$PATH:$(pwd)/polly/bin
    > cd hunter
    > TOOLCHAIN=toolchain PROJECT_DIR=examples/project_name jenkins.py
  """
  _add_polly_path()
  if _is_windows():
    os.environ["HUNTER_BINARY_DIR"] = "C:\HunterTmp"
  os.environ["TOOLCHAIN"] = toolchain
  os.environ["PROJECT_DIR"] = "examples/" + project_name
  cmd = python3_exe() + " jenkins.py"
  _my_run_command(cmd, HUNTER_REPO)


@cli.command()
def hunter_test_docs():
  """
  Tests that the hunter docs build correctly
  """
  _my_run_command("source ./jenkins.sh && ./make.sh", cwd = HUNTER_REPO + "/docs")


def _do_browse_ci():
  hunter_url_github = _get_project_github_url("hunter")
  hunter_repo_name = hunter_url_github.replace("https://github.com/", "")
  url_travis = "https://travis-ci.org/" + hunter_repo_name
  url_appveyor = "https://ci.appveyor.com/project/" + hunter_repo_name
  webbrowser.open(url_travis)
  webbrowser.open(url_appveyor)


@cli.command()
def hunter_push_modifs():
  """
  Push hunter modifs / browse CI results
  """
  test_git_branch = _git_branch(HUNTER_REPO)
  if not test_git_branch.find("test.") == 0:
    print("Your hunter repo should be on a test.[project_name] branch : abort")
    return False
  _my_run_command("git push", cwd = HUNTER_REPO)
  answer = input("open CI results in the browser ? Type y to open them: ")
  if answer == "y":
    _do_browse_ci()


@cli.command()
def hunter_browse_ci():
  """
  open hunter CI results in a browser (travis & appveyor)
  """
  _do_browse_ci()


if __name__ == "__main__":
  cli()
