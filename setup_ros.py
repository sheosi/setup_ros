#!/usr/bin/env pyhton3
import os
from os.path import expanduser
import random
import subprocess
import sys

if subprocess.check_output(["whoami"]).strip().decode("utf-8") == "root":
    sys.exit("You are running this program as root, don't do it. Remove 'sudo'.")

# available features: ros1, ros2, nao
features = {"ros1", "ros2", "nao"}

ros1_dist_mapping = {
    # Ubuntu
    "bionic": "melodic", # Ubuntu 18.04
    "focal": "noetic", # Ubuntu 20.04
    # Debian
    "buster": "noetic", # Debian 10
    "stretch": "melodic", # Debian 9
}

ros2_dist_mapping = {
    # Ubuntu
    "bionic": "eloquent", # Ubuntu 18.04
    "focal": "foxy", # Ubuntu 20.04
    # Debian
    "buster": "foxy", # Debian 10
    "stretch": "dashing" # Debian 9
}

## Common initialization
os.system("sudo apt update")
os.system("sudo apt -y install curl gnupg2 lsb-release")

lsb_rel = subprocess.check_output(["lsb_release", "-sc"]).strip().decode("utf-8")

ros1_distro = ros1_dist_mapping[lsb_rel]
ros2_distro = ros2_dist_mapping[lsb_rel]

if "ros1" in features:
    ## ROS 1
    # Install ROS 1 base
    os.system("sudo sh -c 'echo \"deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main\" > /etc/apt/sources.list.d/ros-latest.list'")
    os.system("sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654")
    os.system("sudo apt update")
    os.system(f"sudo apt -y install ros-{ros1_distro}-desktop")
    os.system("source ~/.bashrc")

    os.system("sudo apt -y install python-rosdep python-rosinstall python-rosinstall-generator python-wstool build-essential")
    os.system("sudo apt -y install catkin")
    os.system("sudo rosdep init")
    os.system("rosdep update")
    #os.system("sudo apt -y autoremove") # Clean all remnants

    # Setup catkin_ws
    os.system("mkdir -p ~/catkin_ws/src")
    os.chdir(expanduser("~") + "/catkin_ws")
    os.system("catkin_make")

    # Install vcstool
    os.system("sudo apt -y install python3-vcstool")

    if "nao" in features:
        if ros1_distro == "melodic":
            # Install Nao things
            os.chdir(expanduser("~") + "/catkin_ws/src")
            
            # Base nao
            os.system(f"sudo apt -y install ros-{ros1_distro}-nao-meshes ros-{ros1_distro}-naoqi-bridge-msgs ros-{ros1_distro}-camera-info-manager ros-{ros1_distro}-octomap-msgs ros-{ros1_distro}-move-base-msgs liboctomap-dev")
            # NaoGazebo
            os.system(f"sudo apt -y install ros-{ros1_distro}-gazebo-ros ros-{ros1_distro}-controller-manager")
            os.system("git clone https://github.com/sheosi/nao_auto_bridge/")
            os.system("git clone https://github.com/ros-naoqi/nao_moveit_config")
            os.system("git clone https://github.com/ros-naoqi/nao_extras")
            os.system("git clone https://github.com/ros-naoqi/naoqi_bridge")
            os.system("git clone https://github.com/ros-naoqi/nao_robot")
            os.system("git clone https://github.com/ros-naoqi/nao_virtual")
            os.system("git clone https://github.com/ros-naoqi/naoqi_driver")
            os.system("git clone https://github.com/ahornung/humanoid_msgs/")
            os.system("git clone https://github.com/ros-naoqi/naoqi_dcm_driver") # Needed for nao_dcm_robot
            os.system("git clone https://github.com/ros-naoqi/nao_dcm_robot") # Needed for moveit + Gazebo
            os.chdir(expanduser("~") + "/catkin_ws/")
            os.system("catkin_make")
            # Much easier just to call rosdep, actually
            os.system(f"rosdep install -i --from-path src --rosdistro {ros1_distro} -y")
        else:
            print("[WARNING] This version is not compatible with Nao, won't be installed")

if "ros2" in features:
    ## ROS 2
    # Make sure we have an UTF-8 compatible system
    os.system("sudo apt update")
    os.system("sudo apt -y install locales")
    os.system("sudo locale-gen es_ES es_ES.UTF-8")
    os.system("sudo update-locale LC_ALL=es_ES.UTF-8 LANG=es_ES.UTF-8")
    os.system("export LANG=es_ES.UTF-8")

    # Install ROS 2 base
    os.system("curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -") # Add key
    os.system("sudo sh -c 'echo \"deb [arch=$(dpkg --print-architecture)] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main\" > /etc/apt/sources.list.d/ros2-latest.list'")
    os.system("sudo apt update")
    os.system(f"sudo apt -y install python3-colcon-common-extensions ros-{ros2_distro}-desktop")

    # Install argcomplete (to have autocompletion)
    os.system("sudo apt -y install python3-pip")
    os.system("pip3 install -U argcomplete")

    # Make ROS 2 development workspace
    os.system("mkdir -p ~/dev_ws/src")

    # Only install bridge if both ROS1 and ROS2 are installed
    if "ros1" in features:
        os.chdir(expanduser("~") + "/dev_ws/src")
        os.system('git clone -b eloquent https://github.com/ros2/ros1_bridge')
        os.system('git clone https://github.com/sheosi/naoqi_bridge_msgs')
        os.system('git clone https://github.com/sheosi/humanoid_msgs')
        os.system('git clone -b ros2 https://github.com/ros-planning/moveit_msgs')
        os.system('sudo apt install -y ros-eloquent-ros-testing')

        # Write function for enabling the bridge
        os.system('echo "\nenable_bridge () {" >> ~/.bashrc')
        os.system('echo "    source ~/bridge_ws/install/local_setup.bash" >> ~/.bashrc')
        os.system('echo "}" >> ~/.bashrc')

    os.chdir(expanduser("~") + "/dev_ws")
    os.system("colcon build")

    ## Set shell functions and variables
    domain_id = random.randint(0,256)
    os.system("echo \"\n# ROS-related settings and funtions\" >> ~/.bashrc")
    os.system(f"echo \"export ROS_DOMAIN_ID={domain_id}\" >> ~/.bashrc")
    os.system(r'echo "echo \"ROS_DOMAIN_ID: \$ROS_DOMAIN_ID\"" >> ~/.bashrc')

if "ros1" in features:
    # Add enable_ros1 function to set-up ros1 env
    os.system("echo \"\nenable_ros1() {\" >> ~/.bashrc")
    os.system(f"echo \"  source /opt/ros/{ros1_distro}/setup.bash\" >> ~/.bashrc")
    os.system("echo \"  source ~/catkin_ws/devel/setup.bash\" >> ~/.bashrc")
    os.system("echo \"}\" >> ~/.bashrc")

if "ros2" in features:
    # Add enable_ros2 function to set-up ros2 env
    os.system("echo \"\nenable_ros2() {\" >> ~/.bashrc")
    os.system(f"echo \"  source /opt/ros/{ros2_distro}/setup.bash\" >> ~/.bashrc")
    os.system("echo \"  source /usr/share/colcon_cd/function/colcon_cd.sh\" >> ~/.bashrc")
    os.system("echo \"  source ~/dev_ws/install/local_setup.bash\" >> ~/.bashrc")
    os.system("echo \"  export _colcon_cd_root=~/ros2_install\" >> ~/.bashrc")
    os.system("echo \"}\" >> ~/.bashrc")

if "ros1" in features and "ros2" in features:
    os.system("echo '\nenable_bridge () {' >> ~/.bashrc")
    os.system("echo 'source ~/bridge_ws/install/local_setup.bash' >> ~/.bashrc")
    os.system("echo '}\n' >> ~/.bashrc")

## Finally, platform-specific fixes
# For VM guests make them use OpenGL 2.1 instead of 3.3 (it works much better)
os.system(r'grep -q ^flags.*\ hypervisor\  /proc/cpuinfo && echo "export SVGA_VGPU10=0" >> ~/.profile')

# Set DISPLAY env variable on WSL
if os.system("grep -q microsoft /proc/version") == 0:
    os.system("sudo apt install -y x11-apps")
    # Each version of WSL requires it's own settings, if a 
    if os.system("grep -q WSL2 /proc/version; echo $?") == 0: # WSL2
        os.system("echo \"\n# WSL2-specfic configuration to connect to the DISPLAY\" >> ~/.bashrc")
        os.system("echo \"export DISPLAY=$(awk '/nameserver / {print $2; exit}' /etc/resolv.conf 2>/dev/null):0\" >> ~/.bashrc")
        os.system("echo \"export LIBGL_ALWAYS_INDIRECT=1\" >> ~/.bashrc")
    else: # WSL1
        os.system("echo \"export DISPLAY=:0.0\" >> ~/.bashrc")

print(f"\n\nYour domain id is {domain_id}, make sure no one has the same")
print("Please do 'source ~/.bashrc' or close this shell and open a new one")