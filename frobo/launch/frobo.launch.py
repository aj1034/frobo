import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


from launch_ros.actions import Node
import xacro


def generate_launch_description():

    robotXacroName='diff_drive_robo'
    namePackage='frobo'
    config_dir = os.path.join(get_package_share_directory('frobo'),'config')
    rviz_config_dir = os.path.join(config_dir,'default.rviz')


    modelFileRelativePath='model/new_stuti_atharva.xacro'
    worldFileRelativePath='worlds/empty_world.world'

    pathModelFile= os.path.join(get_package_share_directory(namePackage), modelFileRelativePath)
    pathWorldFile= os.path.join(get_package_share_directory(namePackage), worldFileRelativePath)

    robotDescription= xacro.process_file(pathModelFile).toxml()

    gazebo_rosPackageLaunch =  PythonLaunchDescriptionSource(os.path.join(get_package_share_directory('gazebo_ros'),'launch','gazebo.launch.py'))

    #gazebo_params_file = os.path.join(get_package_share_directory(namePackage),'config','gazebo_params.yaml')  'extra_gazebo_args': '--ros-args --params-file ' + gazebo_params_fil
    gazeboLaunch = IncludeLaunchDescription(gazebo_rosPackageLaunch, launch_arguments={'world' : pathWorldFile}.items())


    spawnModelNode = Node( 
        package='gazebo_ros', 
        executable='spawn_entity.py', 
        arguments = ['-topic','robot_description','-entity', robotXacroName], 
        output = 'screen')

    nodeRSP = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robotDescription, 'use_sim_time':True}]
        )
    
    rvizNode = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2_node',
        arguments=['-d', rviz_config_dir],
        output='screen'
    )
    
    diff_contNode = Node(
        package='controller_manager',
        executable='spawner',
        output='screen',
        arguments=['diff_cont']
    )

    joint_broadNode = Node(
        package='controller_manager',
        executable='spawner',
        output='screen',
        arguments=['joint_broad']
    )


    twist_mux_params = os.path.join(get_package_share_directory(namePackage),'config','twist_mux.yaml')
    twist_mux = Node(
            package="twist_mux",
            executable="twist_mux",
            parameters=[twist_mux_params, {'use_sim_time': True}],
            remappings=[('/cmd_vel_out','/diff_cont/cmd_vel_unstamped')]
        )

    launchDescriptionObject = LaunchDescription()

    launchDescriptionObject.add_action(gazeboLaunch)
    launchDescriptionObject.add_action(spawnModelNode)
    launchDescriptionObject.add_action(nodeRSP)
    launchDescriptionObject.add_action(rvizNode)
    launchDescriptionObject.add_action(diff_contNode)
    launchDescriptionObject.add_action(joint_broadNode)  
    launchDescriptionObject.add_action(twist_mux)  

    return launchDescriptionObject









   
