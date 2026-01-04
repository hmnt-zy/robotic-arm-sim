from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, LogInfo
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution,FileContent
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import os


def generate_launch_description():
    # use_sim_time = true for using gazebo time 
    use_sim_time='true'
    # urdf_path = path of the urdf can be dynamically given when launching this file
    urdf_path=LaunchConfiguration('urdf_path', default=PathJoinSubstitution([FindPackageShare('arm_description'),'urdf', 'robot_model_6_dof.urdf.xacro']))
    # world_location = path to the world file as per task= empty_world.sdf
    world_location='empty.sdf'
    # bridge_params = path to the bridge file for bridging topics ROS <-> GZ
    bridge_params=os.path.join(FindPackageShare('arm_gazebo').find('arm_gazebo'),'config','arm_bridge_parameters.yaml')
    
    # Start Gazebo using ros_gz_sim launch
    start_gazebo_world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            ])
        ]),
        launch_arguments={
            'gz_args':[' ',world_location],
            'on_exit_shutdown':'true'
            }.items()
            )
    # Spawn the robot model using create node in ros_gz_sim package
    create_entity =Node(
        package='ros_gz_sim',
        executable='create',
        name='spawnentity',
        arguments=[
            '-name', 'tortoisebot',
            '-topic','robot_description',
            #'-file', urdf_path,
            #'-z', '2' #,'-x','1'
            ],
            output='screen'
            )
    # start the gazebo ros bridge node
    gazebo_ros_bridge=Node(
        package='ros_gz_bridge',
		executable='parameter_bridge',
		arguments=[
            '--ros-args','-p', f'config_file:={bridge_params}' #bridge config file
            ],output='screen'
            )
    # start rviz launch file from
    rviz_launch_file=IncludeLaunchDescription(
        PathJoinSubstitution([FindPackageShare('urdf_tutorial'),'launch','robot_6_dof.launch.py']),
        launch_arguments={'use_sim_time':use_sim_time,'urdf_path':urdf_path}.items()) # urdf path given as argument

    return LaunchDescription([
        start_gazebo_world,
        create_entity,
        rviz_launch_file,
        gazebo_ros_bridge,
    ])
