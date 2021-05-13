# !/home/hvh/miniconda3/envs/ADS/bin/python

from lego_robot import *
from slam_b_library import filter_step, compute_cartesian_coordinates
from project_landmarks import write_cylinders

# SUBSAMPLING
# Takes one scan and subsamples the measurements, so that every sampling'th point is taken. 
# Returns a list of (x, y) points in the scanner's coordinate system.

def get_subsampled_points(scan, sampling = 10):
    # Subsample from scan
    index_range_tuples = []
    for i in xrange(0, len(scan), sampling):
        index_range_tuples.append( (i, scan[i]) )
    return compute_cartesian_coordinates(index_range_tuples, 0.0)

# Get corresponding pair on the wall for every subsampled data point
# Given a set of points, checks for every point p if it is closer than eps to the left, right, upper or lower wall of the arena. 
# If so, adds the point to left_list, and the closest point on the wall to right_list.

def get_corresponding_points_on_wall(points,
                                     arena_left = 0.0, arena_right = 2000.0,
                                     arena_bottom = 0.0, arena_top = 2000.0,
                                     eps = 150.0):
    left_list = []
    right_list = []
    x = 0
    y = 0

    for (x, y) in points:

        if(x <= eps):
            left_list.append((x, y))
            right_list.append((0, y))
        elif(x >= (arena_right - eps)):
            left_list.append((x, y))
            right_list.append((arena_right, y))
        elif(y >= (arena_top-eps)):
            left_list.append((x, y))
            right_list.append((x, arena_top))
        elif(y <= (arena_bottom+eps)):
            left_list.append((x, y))
            right_list.append((x, 0))

    return left_list, right_list


if __name__ == '__main__':
    # The constants we used for the filter_step.
    scanner_displacement = 30.0
    ticks_to_mm = 0.349
    robot_width = 150.0

    # The start pose we obtained miraculously.
    pose = (1850.0, 1897.0, 3.717551306747922)

    # Read the logfile which contains all scans.
    logfile = LegoLogfile()
    logfile.read("Logs/robot4_motors.txt")
    logfile.read("Logs/robot4_scan.txt")

    # Iterate over all positions.
    out_file = file("logs/find_wall_pairs.txt", "w")
    for i in xrange(len(logfile.scan_data)):
        # Compute the new pose.
        pose = filter_step(pose, logfile.motor_ticks[i],
                           ticks_to_mm, robot_width,
                           scanner_displacement)

        # Subsample points.
        subsampled_points = get_subsampled_points(logfile.scan_data[i])
        world_points = [LegoLogfile.scanner_to_world(pose, c)
                        for c in subsampled_points]

        # Get corresponding points on wall.
        left, right = get_corresponding_points_on_wall(world_points)

        # Write to file.
        # The pose.
        out_file.write("F %f %f %f\n" % pose)
        # Write the scanner points and corresponding points.
        write_cylinders(out_file, "W C", left + right)

    out_file.close()
