#!/usr/bin/python3

from porting_helper import *

drm = [
	'drivers/gpu/drm',
	'include/drm',
	'include/uapi/drm',
]

helper = PortingHelper()

# Create a patch-id filter using v4.9 maintenance branch
maint_49 = helper.commits(rev='v4.9..v4.9.36', paths=drm)
filter = PatchIdFilter(maint_49)

# Find out DRM commits up to v4.12, which is not back ported to v4.9-maint
master = helper.commits(rev='v4.9..v4.12', paths=drm, filters=[filter])

print('Not ported:', len(master), 'commits')

