import os, sys, argparse
from FATtools import vhdutils, vhdxutils, vdiutils, vmdkutils
from FATtools.utils import is_vdisk


def create_parser(parser_create_fn=argparse.ArgumentParser,parser_create_args=None):
    par = parser_create_fn(*parser_create_args,description="Create a blank disk device of a given size")
    par.add_argument('image_file',help="The image file or disk device to write to",metavar="IMAGE_FILE")
    par.add_argument("-s", "--size", dest="image_size", help="specify virtual disk size. K, M, G or T suffixes accepted", metavar="SIZE",required=True)
    par.add_argument("-b", "--base", dest="base_image", help="specify a virtual disk image base to create a differencing image with default parameters", metavar="BASE")
    par.add_argument("-f", "--force", dest="force", help="overwrites a pre-existing image", action="store_true", default=False)
    return par

def call(args):
    if args.base_image:
        modules = {'.vhd':vhdutils, '.vhdx':vhdxutils, '.vdi':vdiutils, '.vmdk':vmdkutils}
        delta = is_vdisk(args.image_file)
        if not delta:
            print("mkvdisk error: you must specify a differencing disk image file name (invalid extension?)")
            par.print_help()
            sys.exit(1)
        base = is_vdisk(args.base_image)
        if not base:
            print("mkvdisk error: you must specify a valid base image to create a differencing disk!")
            par.print_help()
            sys.exit(1)
        m = modules[os.path.splitext(base)[1].lower()]
        m.mk_diff(delta, base, overwrite=('no','yes')[args.force])
        print("Differencing image '%s' created and linked with base '%s'"%(delta,base))
        sys.exit(0)

    if not args.image_size:
        print("mkvdisk error: you must specify a virtual disk image size!")
        par.print_help()
        sys.exit(1)

    u = args.image_size[-1].lower()
    if u in ('k','m','g','t'):
        fssize = int(args.image_size[:-1]) * (1<<{'k':10,'m':20,'g':30,'t':40}[u])
    else:
        fssize = int(args.image_size)

    if os.path.exists(args.image_file) and not args.force:
        print("mkvdisk error: disk image already exists, use -f to force overwriting")
        sys.exit(1)

    s = args.image_file.lower()
    if not s.endswith('.vhd') and not s.endswith('.vhdx') and not s.endswith('.vdi') and not s.endswith('.vmdk'):
        print("Creating RAW disk image '%s'... "%args.image_file, end='')
        f=open(args.image_file, 'wb');f.seek(fssize-1);f.write(b' ');f.close()
        print("OK!")
        sys.exit(0)

    if s.endswith('.vhd'):
        fmt = vhdutils
    elif s.endswith('.vhdx'):
        fmt = vhdxutils
    elif s.endswith('.vdi'):
        fmt = vdiutils
    else:
        fmt = vmdkutils

    fmt.mk_dynamic(args.image_file, fssize, overwrite='yes')
    print("Virtual disk image '%s' created."%args.image_file)

if __name__ == '__main__':
    par=create_parser()
    args = par.parse_args()
    call(args)
