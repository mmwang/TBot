import time
import struct

import Quartz.CoreGraphics as CG


class ScreenPixel(object):
    def capture(self, region = None):
        if region is None:
            region = CG.CGRectInfinite
        else:
            if region.size.width % 2 > 0:
                emsg = "Capture region width should be even (was %s)" % (
                    region.size.width)
                raise ValueError(emsg)

        image = CG.CGWindowListCreateImage(
            region,
            CG.kCGWindowListOptionOnScreenOnly,
            CG.kCGNullWindowID,
            CG.kCGWindowImageDefault)

        prov = CG.CGImageGetDataProvider(image)

        self._data = CG.CGDataProviderCopyData(prov)

        self.width = CG.CGImageGetWidth(image)
        self.height = CG.CGImageGetHeight(image)

    def pixel(self, x, y):

        data_format = "BBBB"
        offset = 4 * ((self.width*int(round(y))) + int(round(x)))
        b, g, r, a = struct.unpack_from(data_format, self._data, offset=offset)
        return (r, g, b, a)


if __name__ == '__main__':

    sp = ScreenPixel()

    region = CG.CGRectMake(242, 440, 400, 400)
    sp.capture(region=region)

    print sp.width, sp.height
    print sp.pixel(0, 0)

    from pngcanvas import PNGCanvas
    c = PNGCanvas(sp.width, sp.height)
    for x in range(sp.width):
        for y in range(sp.height):
            c.point(x, y, color = sp.pixel(x, y))

    with open("test.png", "wb") as f:
        f.write(c.dump())
