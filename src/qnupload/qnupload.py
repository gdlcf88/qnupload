#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This modle will help you put your local file to
QiNiu cloud storage, I use it to share files and
pictures in my blog.
"""
import argparse
# Compatible for Py2 and Py3
try:
    import ConfigParser
except ImportError:
    import configparser
import os
import qiniu.config
import sys

from qiniu import Auth
from qiniu import BucketManager

conf_file = "/etc/qnupload/qnupload.conf"


def getAuth(accessKey, secretKey):
    """Get the auth object by access key and secret key."""
    auth = Auth(accessKey, secretKey)

    return auth


def uploadFile(bucketName, filePath, auth, domain, full_name):
    """Upload file to your bucket on qiniu server."""
    # Compatible for Py2 and Py3
    if full_name:
        file_basename = filePath
    else:
        file_basename = os.path.basename(filePath)

    try:
        fileName = file_basename.decode("utf-8")
    except AttributeError:
        fileName = file_basename

    up_token = auth.upload_token(bucketName)
    ret, resp = qiniu.put_file(up_token, fileName, filePath)
    if ret:
        print("Upload file: %s" % (filePath))
        print("Link: %s" % (domain + fileName))
    else:
        print("Failed to upload file.")
        print(resp)


def getBucket(uploadAuth):
    """Get the bucket object."""

    return BucketManager(uploadAuth)


def checkFile(bucket, filePath, bucketName):
    """Check the file path is right and if it is exist in the bucket."""
    if not os.path.exists(filePath):
        print("Wrong file path: %s" % (filePath))
        return False

    ret, info = bucket.stat(bucketName, filePath)
    if ret:
        print("File exists in Qiniu cloud: %s" % (filePath))
    return ret is None


def check_conf(conf_file):
    """Check the configure file is existed."""
    if not os.path.exists(conf_file):
        print("ERROR: Cannot find configure file.")
        print("Please create configure file: %s" % (conf_file))
        print("[DEFAULT]")
        print("default_bucket_name =")
        print("access_key =")
        print("secret_key =")
        print("domain =")

        sys.exit(1)


def main():
    # Check the configure file
    check_conf(conf_file)

    # Read configure file
    # Compatible for Py2 and Py3
    try:
        cf = ConfigParser.ConfigParser()
    except NameError:
        cf = configparser.ConfigParser()
    cf.read(conf_file)

    parser = argparse.ArgumentParser(
            prog="quupload",
            description="This is a tool to upload file to Qiniu cloud.")
    parser.add_argument("file",
                        metavar="filepath",
                        nargs='+',
                        help="Specify a file to upload to Qiniu cloud.")
    parser.add_argument("-b", "--bucket",
                        help="A bucket under your Qiniu account.")
    parser.add_argument("-a", "--access-key",
                        help="Your access key.")
    parser.add_argument("-s", "--secret-key",
                        help="Your secret key.")
    parser.add_argument("-d", "--domain",
                        help="The domain of your Qiniu account to share \
                              the file you upload to Qiniu cloud.")
    parser.add_argument("--full-name",
                        action='store_true',
                        help="The file will be named with the path as \
                             its prefix when specify this option. ")

    args = parser.parse_args()

    if args.bucket is None:
        bucketName = cf.get("DEFAULT", "default_bucket_name")
    else:
        bucketName = args.bucket

    if args.access_key is None:
        access_key = cf.get("DEFAULT", "access_key")
    else:
        access_key = args.access_key

    if args.secret_key is None:
        secret_key = cf.get("DEFAULT", "secret_key")
    else:
        secret_key = args.secret_key

    if args.domain is None:
        domain = cf.get(bucketName, "domain")
    else:
        domain = args.domain

    full_name = args.full_name

    # Parse domain
    domain = domain + "/"
    if not domain.startswith("http"):
        domain = "http://" + domain

    # Get the full file list from the command line
    fileList = []
    for item in args.file:
        if os.path.isdir(item):
            fileList.extend([item+'/'+f for f in os.listdir(item)])
        elif os.path.isfile(item):
            fileList.append(item)

    uploadAuth = getAuth(access_key, secret_key)
    bucket = getBucket(uploadAuth)
    for filePath in fileList:
        if checkFile(bucket, filePath, bucketName):
            uploadFile(bucketName, filePath, uploadAuth, domain, full_name)

if __name__ == '__main__':
    main()
