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

THISDIR = os.path.dirname(os.path.realpath(__file__)) + "/"
MAIN_REPO = THISDIR
HUNTER_REPO = os.path.realpath( MAIN_REPO + "/hunter/") + "/"


@click.group()
def cli():
  """
  This script tries to simplify most of the manual actions described in
  https://docs.hunter.sh/en/latest/creating-new/create/cmake.html

  \b
  Info about hunter branching model:
    * branch pr.project_name = pull request candidate for hunter repo
            (https://github.com/ruslo/hunter)
    * branch pr.pkg.project_name = pull request candidate for hunter package testing templates
            (https://github.com/ingenue/hunter)
            this branch shall contains only modifications to appveyor.yml and .travis.yml
    * branch test.project_name = this branch contains all the modifications
      (packages and version + appveyor/travis)
      This branch can be pushed to your own fork of hunter, so that you can test
      the build through Appveyor and Travis.

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


@cli.command()
@click.argument("project_name", required=True)
@click.option("--clean/--no-clean", default = False)
def test_build(project_name: Folder, clean):
  """
  \b
  Helps to build a project using hunter.

  The project must be a subfolder of this repo).
  Basically it does this

  \b
  cd project-name
  cmake .. -GNinja -DHUNTER_ENABLED=ON
  ninja
  """
  app_folder = MAIN_REPO + project_name
  build_folder = app_folder + "/build"
  if clean:
    if os.path.isdir(build_folder):
      shutil.rmtree(build_folder)
  if not os.path.isdir(build_folder):
    os.mkdir(build_folder)
  _my_run_command("cmake .. -GNinja -DHUNTER_ENABLED=ON", build_folder)
  _my_run_command("ninja", build_folder)


def _add_polly_path():
  polly_bin_path = ":{}polly/bin".format(MAIN_REPO)
  os.environ["PATH"] = os.environ["PATH"] + ":" + polly_bin_path


@cli.command()
def hunter_list_toolchains():
  """
  Lists hunter toolchains (polly.py --help)
  """
  _add_polly_path()
  _my_run_command("polly.py --help", HUNTER_REPO)


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


@cli.command()
def hunter_prepare_release():
  """
  Prepare a release for hunter

  \b
  What it does:
  * Checks that your hunter submodule status is clean
  * Checks that your hunter submodule status is on a test.[project_name] branch
  * Prepare hunter branch "pr.project_name":
    This branch will be identical to your current branch, except that
    it will reset the modification to appveyor.yml and .travis.yml so that they match
    the version of hunter master branch
    (This branch must have been created manually)
  * Force push the branch pr.project_name to github
  * Return you to the branch test.project_name
  """
  # Checks that your hunter submodule status is clean
  if not _is_git_repo_clean(HUNTER_REPO):
    print("Your hunter repo is not clean : abort")
    return False
  # Checks that your hunter submodule status is on a test.[project_name] branch
  test_git_branch = _git_branch(HUNTER_REPO)
  if not test_git_branch.find("test.") == 0:
    print("Your hunter repo should be on a test.[project_name] branch : abort")
    return False
  project_name = test_git_branch.split(".")[1]
  print("project_name = " + project_name)
  print("test_git_branch = " + test_git_branch)
  # Prepare hunter branch "pr.project_name":
  #   This branch will be identical to your current branch, except that
  #   it will reset the modification to appveyor.yml and .travis.yml so that they match
  #   the version of hunter master branch
  pr_pkg_git_branch = "pr.pkg." + project_name
  print("pr_pkg_git_branch = " + pr_pkg_git_branch)

  print("About to run these commands (in order, in subrepo hunter)")
  print("*********************************************************")
  commands = [
    "git branch -D {} || true # ==> *delete* old branch !".format(pr_pkg_git_branch),
    "git checkout -b {} # ==> *recreate* branch from scratch!".format(pr_pkg_git_branch),
    "rm appveyor.yml && rm .travis.yml # ===> ({} should not contain travis/appveyor.yml".format(pr_pkg_git_branch),
    "cp ../travis-hunter-master.yml .travis.yml #  ==> copy .travis.yml from master",
    "git add .travis.yml appveyor.yml && git commit -m \"use master branch .travis.yml\" #   ==> git commit !",
    "git push origin {} --force -u #   ==> git push force !".format(pr_pkg_git_branch),
    "git checkout {} #   ==> return to the test branch !".format(test_git_branch)
  ]
  i = 1
  for cmd in commands:
    print("            {}. {}".format(i, cmd))
    i = i + 1


  i = 1
  for cmd in commands:
    print("About to run : \n")
    print("            {}. {}".format(i, cmd))
    i = i + 1
    answer = input("Really do it ? Type y to confirm: ")
    if answer == "y":
      _my_run_command(cmd, HUNTER_REPO)


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

  test_git_branch = _git_branch(HUNTER_REPO)
  if not test_git_branch.find("test.") == 0:
    print("Your hunter repo should be on a test.[project_name] branch : abort")
    return False
  project_name = test_git_branch.split(".")[1]
  pr_pkg_git_branch = "pr.pkg." + project_name
  print("project_name = " + project_name)
  print("test_git_branch = " + test_git_branch)
  print("pr_pkg_git_branch = " + pr_pkg_git_branch)

  release_url, sha1 = _project_create_release_do_release(
    hunter_project_name="hunter",
    release_name=release_name,
    target_branch=pr_pkg_git_branch
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
  cmd = "TOOLCHAIN={} PROJECT_DIR=examples/{} ./jenkins.py".format(toolchain, project_name)
  _my_run_command(cmd, HUNTER_REPO)


@cli.command()
def hunter_browse_ci():
  """
  open hunter CI results in a browser (travis & appveyor)
  """
  hunter_url_github = _get_project_github_url("hunter")
  hunter_repo_name = hunter_url_github.replace("https://github.com/", "")
  url_travis = "https://travis-ci.org/" + hunter_repo_name
  url_appveyor = "https://ci.appveyor.com/project/" + hunter_repo_name
  webbrowser.open(url_travis)
  webbrowser.open(url_appveyor)


if __name__ == "__main__":
  cli()
