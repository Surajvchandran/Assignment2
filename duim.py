#!/usr/bin/env python3

import subprocess, sys
import os
import argparse

'''
OPS445 Assignment 2 - Winter 2024
Program: duim.py
Author: svchandran
The python code in this file (duim.py) is original work written by
svchandran. No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or on-line resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: This script is an improved version of the du command.
It displays disk usage information for directories with bar graphs
representing the percentage of space each subdirectory occupies.
The script supports human-readable output format and customizable
bar graph length.

Date: April 11, 2025
'''

def parse_command_args():
    """
    Set up argparse here. Call this function inside main.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="DU Improved -- See Disk Usage Report with bar charts",
        epilog="Copyright 2022"
    )
    
    parser.add_argument("-l", "--length", type=int, default=20, 
                        help="Specify the length of the graph. Default is 20.")
    
    # Add human-readable argument
    parser.add_argument("-H", "--human-readable", action="store_true",
                        help="print sizes in human readable format (e.g. 1K 23M 2G)")
    
    # Add target directory argument
    parser.add_argument("target", nargs="?", default=".",
                        help="The directory to scan.")
    
    return parser.parse_args()


def percent_to_graph(percent, total_chars):
    """
    Returns a string representing a bar graph based on percentage.
    
    Args:
        percent (float): Percentage value between 0 and 100
        total_chars (int): Total number of characters in the bar graph
        
    Returns:
        str: Bar graph string with = for filled portion and spaces for empty
    """
    # Validate percent is between 0 and 100
    if not 0 <= percent <= 100:
        raise ValueError("Percent must be between 0 and 100")
    
    # Calculate number of filled characters
    filled_chars = round(percent * total_chars / 100)
    
    # Create bar graph string
    graph = '=' * filled_chars + ' ' * (total_chars - filled_chars)
    
    return graph


def call_du_sub(location):
    """
    Takes the target directory as an argument and returns a list of strings
    returned by the command `du -d 1 location`.
    
    Args:
        location (str): Path to the target directory
        
    Returns:
        list: Output of du command as a list of strings
    """
    process = subprocess.Popen(['du', '-d', '1', location], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE, 
                              universal_newlines=True)
    
    stdout, stderr = process.communicate()
    
    # Split by newlines and remove empty strings
    result = [line for line in stdout.split('\n') if line]
    
    return result


def create_dir_dict(alist):
    """
    Gets a list from call_du_sub, returns a dictionary which should have full
    directory name as key, and the number of bytes in the directory as the value.
    
    Args:
        alist (list): Output from call_du_sub() function
        
    Returns:
        dict: Dictionary with directory paths as keys and sizes (in bytes) as values
    """
    dir_dict = {}
    
    for line in alist:
        # Split by whitespace - first item is size, rest is path
        parts = line.split()
        if len(parts) < 2:
            continue
            
        size = int(parts[0])  
        path = ' '.join(parts[1:])  
        
        dir_dict[path] = size
        
    return dir_dict


def human_readable_size(size_bytes):
    """
    Convert size in bytes to human readable format.
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Size in human readable format (e.g., 10.8 M)
    """
    units = ['B', 'K', 'M', 'G', 'T', 'P']
    
    index = 0
    size = float(size_bytes)
    
    while size >= 1024 and index < len(units) - 1:
        size /= 1024
        index += 1
    
    # Format the size with one decimal place
    return f"{size:.1f} {units[index]}"


def print_directory_info(dir_dict, total_size, target_dir, human_readable, bar_length):
    """
    Print formatted directory information.
    
    Args:
        dir_dict (dict): Dictionary with directory paths and sizes
        total_size (int): Total size of the target directory
        target_dir (str): Path to the target directory
        human_readable (bool): Whether to show sizes in human readable format
        bar_length (int): Length of the bar graph
    """
    # Sort directories by size (largest first)
    sorted_dirs = sorted(dir_dict.items(), key=lambda x: x[1], reverse=True)
    
    # Print each subdirectory
    for dir_path, size in sorted_dirs:
        if dir_path == target_dir:
            continue
        
        # Calculate percentage
        percent = (size / total_size) * 100
        
        # Create bar graph
        bar = percent_to_graph(percent, bar_length)
        
        # Format size
        if human_readable:
            size_str = human_readable_size(size)
        else:
            size_str = str(size)
        
        # Print formatted output
        print(f"{percent:3.0f} % [{bar}] {size_str:8} {dir_path}")
    
    # Print total
    if human_readable:
        total_str = human_readable_size(total_size)
    else:
        total_str = str(total_size)
    
    print(f"Total: {total_str}   {target_dir}")


def main():
    """Main function to run the script."""
    # Parse command line arguments
    args = parse_command_args()
    
    if not os.path.isdir(args.target):
        print(f"Error: {args.target} is not a valid directory")
        sys.exit(1)
    
    # Get directory information
    du_output = call_du_sub(args.target)
    dir_dict = create_dir_dict(du_output)
    
    target_dir = args.target
    if target_dir not in dir_dict:
        last_line = du_output[-1]
        parts = last_line.split()
        target_dir = ' '.join(parts[1:])
    
    # Get total size
    total_size = dir_dict[target_dir]
    
    # Format and print results
    print_directory_info(dir_dict, total_size, target_dir, args.human_readable, args.length)


if __name__ == "__main__":
    main()
