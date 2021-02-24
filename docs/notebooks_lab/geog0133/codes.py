import pandas as pd
import numpy as np
import gdal
import matplotlib.pylab as plt
import matplotlib.animation as animation
from IPython.display import IFrame
from IPython.display import HTML
from osgeo import osr
import fiona
import scipy.stats
import datetime

def world2Pixel(geoMatrix, x, y):
  """
  Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
  the pixel location of a geospatial coordinate
  """
  ulX = geoMatrix[0]
  ulY = geoMatrix[3]
  xDist = geoMatrix[1]
  yDist = geoMatrix[5]
  rtnX = geoMatrix[2]
  rtnY = geoMatrix[4]
  pixel = ((x - ulX) / xDist)
  line = ((ulY - y) / xDist)
  return np.array([pixel, line]).astype(int)

def read_ba(ifile,shp,cf):

  # read fire day dataset
  # read burned area dataset
  dateFile = f'HDF4_EOS:EOS_GRID:"{ifile}":MOD_GRID_Monthly_500km_BA:burndate'
  dataset = gdal.Open(dateFile)
  dateData = dataset.ReadAsArray().astype(float)
  ba_qa = gdal.Open(f'HDF4_EOS:EOS_GRID:"{ifile}":MOD_GRID_Monthly_500km_BA:ba_qa').ReadAsArray()
  vmin,vmax = np.nanmin(dateData[dateData>0]),np.nanmax(dateData[dateData<400])

  # get projection information
  wkt = dataset.GetProjection()
  geoMatrix = dataset.GetGeoTransform()
  wide = dataset.RasterXSize
  high = dataset.RasterYSize

  # set up transformation from 
  # lat/long to MODIS image coordinates
  p1 = osr.SpatialReference()
  p1.ImportFromWkt(wkt)
  p2 = osr.SpatialReference()
  p2.ImportFromEPSG(4326)
  transform = osr.CoordinateTransformation(p2,p1)

  # remove non-data values
  # but show the sea as value 400
  dateData[dateData>365]=400
  dateData[dateData==0]=np.nan

  # read FIRMS fire coordinates from shapefile
  shape = fiona.open(shp)
  lon = np.array([i[1]['properties']['LONGITUDE'] for i in shape.items()])
  lat = np.array([i[1]['properties']['LATITUDE'] for i in shape.items()])

  # and convert to image coordinates
  image_space = np.array([transform.TransformPoint(*x) for x in zip(lon,lat)])[:,:2].T
  pix = world2Pixel(geoMatrix, *image_space)

  # coordinate limits:
  y0,y1 = np.max([0,pix[1].min()]),np.min([high,pix[1].max()])
  x0,x1 = np.max([0,pix[0].min()]),np.min([wide,pix[0].max()])  

  # first find the data points within spatial bounds
  c0=np.logical_and(pix[0]>=x0,pix[1]>=y0)
  c1=np.logical_and(pix[0]<x1,pix[1]<y1)
  ok=np.logical_and(c1,c0)

  # get the burned area data values
  # for the FIRMS fires
  ba_values = dateData[pix[:,ok][0],pix[:,ok][1]]
  ba_qc = ba_qa[pix[:,ok][0],pix[:,ok][1]]

  # get the day of year and conbfidence for FIRMS
  acq = np.array([i[1]['properties']['ACQ_DATE'] \
                for i in shape.items()])
  confidence = np.array([i[1]['properties']['CONFIDENCE'] \
                for i in shape.items()])
  doy = np.array([datetime.datetime.strptime(i,'%Y-%m-%d')\
                .timetuple().tm_yday for i in acq])[ok]

  # nans and invalid
  bad = np.logical_or(np.isnan(ba_values),ba_values>365)
  # and confidence
  bad = np.logical_or(confidence[ok]<cf,bad)
  # and qa
  bad = np.logical_or(ba_qc>1,bad)
  ndays = vmax-vmin
  

  return dateData,(ndays,vmin,vmax),(doy,ba_values,bad),(pix,x0,x1,y0,y1)


