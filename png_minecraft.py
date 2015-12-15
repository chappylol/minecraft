#!/usr/bin/python2.7

import os
import sys
import re
import pdb
from collections import defaultdict,OrderedDict
from PIL import Image, ImageChops
import scipy.spatial as sp

BASEIMAGE = sys.argv[1]

ROOTDIR = None
#ROOTDIR = sys.argv[2]

import re
point_table = ([0] + ([255] * 255))

#search minecraft directory for .pngs

def find_images(fromfile=None):

    images = {}
    if fromfile:
        filelist = open(fromfile, 'r')
        for filepath in filelist:
            filepath = filepath.strip()
            try:
                fh = Image.open(filepath.strip())
            except:
                #print "Bad: %s" % (filepath)
                continue

            size = fh.size

            if size[0] < 16 or size[1] < 16:
                continue
                    
            elif size[0] != 16 or size[1] != 16:
                fh = fh.crop((0,0,16,16))

            images[filepath] = fh
        return images


    for root, subFolders, files in os.walk(ROOTDIR):
        for file in files:
            if re.search('\.png$', file):
                filepath = os.path.join(root, file)
                if '3D' not in filepath:
                    continue
                fh = Image.open(filepath)
                size = fh.size

                if size[0] < 16 or size[1] < 16:
                    continue
                    
                elif size[0] != 16 or size[1] != 16:
                    fh = fh.crop((0,0,16,16))

                images[filepath] = fh

    return images

def get_chunk(cropped, all_images):
    #new_image = Image.new('RGB',(16,16))
    new_image = []
    file_pixel_map = OrderedDict()
    for x in range(0,16):
        for y in range(0,16):
            input_color = cropped.getpixel((x,y))
            for filename,image in all_images.items():
                raw_pixel = image.getpixel((x,y))
                if type(raw_pixel) != tuple:
                    continue

                #remove alpha - needs better fix.
                pixel = raw_pixel[0:3]

                file_pixel_map[filename] = pixel
    
            tree = sp.KDTree(file_pixel_map.values()) 
            distance, result = tree.query(input_color) 
            nearest_color = file_pixel_map.keys()[result]
            new_image.append(((x,y), nearest_color))
            
    return new_image

def parse_chunk(chunk):
    chunk_strs = []
    for xy, filename in chunk:
        x, y = xy
        filename_split = re.split('/', filename)

        if "blocks" not in filename_split:
            continue

#for example: '/home/matt/assets/botania/textures/blocks/pillarManaQuartz0.png')
        blocks_pivot = filename_split.index("blocks")
        mod_name = filename_split[blocks_pivot - 2]
        mod_path = filename_split[blocks_pivot + 1]
        mod_path = re.sub('\.png.*$','', mod_path)

        mins = "%s,%s,%s" % (x,y,1)
        maxes = "%s,%s,%s" % (x,y,16)
        mod_string = "%s:%s" % (mod_name, mod_path)
        pixel_str = "    { %s,%s,texture=\"%s\"}," % (mins, maxes, mod_string)

        chunk_strs.append(pixel_str)

    #remove last ,
    chunk_strs[-1] = chunk_strs[-1][:-1] #remove comma
    return chunk_strs

def make_2dblock_str(chunk_str):
    block_str = chunk_str

    block_str.insert(0,"{")
    block_str.insert(1,"  shapes={")

    block_str.append("  }")
    block_str.append("}")
       
    for i in block_str:
        print i

XRATIO=6
YRATIO=7

XSIZE = XRATIO*16
YSIZE = YRATIO*16

#The stuff
base_image = Image.open(BASEIMAGE)
base_image.resize((XSIZE,YSIZE))

all_images = find_images('/tmp/filelist_random.txt')

for xchunk in range(0,XRATIO+1):
    for ychunk in range(0,YRATIO+1):
        x16 = xchunk*16
        y16 = ychunk*16
        chunk_dims = (x16, y16, x16+16, y16+16)
        chunk_base = base_image.crop(chunk_dims)

        chunk = get_chunk(chunk_base, all_images)
        parsed_chunk = parse_chunk(chunk)

        make_2dblock_str(parsed_chunk)
        sys.exit(0)

        #chunk_file = open('/tmp/%s%s.png' % (xchunk,ychunk), 'w')
        #chunk.save(chunk_file)
        #chunk_file.close()
