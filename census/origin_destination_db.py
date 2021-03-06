from .census_db import *

class OriginDestinationDB(CensusDB):

  # some constants about the database table
  tbl = 'origindestination'

  def GetOriginsInCounty(self, ctycode):
    destinationSQL = "SELECT distinct od.h_geocode FROM origindestination od join xwalk x on od.h_geocode = x.block2010 WHERE x.cty=?"
    result, destinations = self.select_many(destinationSQL, ctycode)
    return destinations

  def GetOriginsInZipcode(self, zctacode):
    destinationSQL = "SELECT distinct od.h_geocode FROM origindestination od join xwalk x on od.h_geocode = x.block2010 WHERE x.zcta=?"
    result, destinations = self.select_many(destinationSQL, zctacode)
    return destinations

  def GetDestinations(self, origingeoid):
    
    destinationSQL = "SELECT w_geocode FROM origindestination WHERE h_geocode=?"
    result, destinations = self.select_many(destinationSQL, origingeoid)
    return destinations

  def GetDestinationGeoIds(self, origingeoid):

    destinationSQL = "SELECT w_geocode FROM origindestination WHERE h_geocode=?"
    result, destinations = self.select_many(destinationSQL, origingeoid)
    return destinations

  def GetOriginGeoIds(self, destinationgeoid):

    destinationSQL = "SELECT h_geocode FROM origindestination WHERE w_geocode=?"
    result, origins = self.select_many(destinationSQL, destinationgeoid)
    return origins

  # Return the full data for each OD record for the destination (w_geocode)
  # specified in the request.  Values include the h_geocode and the
  # suite of 9 census characterstic bins
  def GetOriginFullData(self, destinationgeoid):

    destinationSQL = "SELECT h_geocode, s000, sa01, sa02, sa03, se01, se02, se03, si01, si02, si03" \
                     " FROM origindestination WHERE w_geocode=?"
    result, origins = self.select_many(destinationSQL, destinationgeoid)
    return origins

  def GetProcessedGeoID(self):
    geoidsSQL = "SELECT geoid, geometry FROM block_centroid_intersection"
    result, geoids = self.select_many(geoidsSQL)
    geoidDict = {}
    for geoidsgeometry in geoids:
      geoidDict[geoidsgeometry[0]] = geoidsgeometry[1]
    return geoidDict

  def GetProcessedGeoIDsOSM(self):
    geoidsSQL = "SELECT geoid, lat_long_end FROM nearest_street_node_info"
    result, geoids = self.select_many(geoidsSQL)
    geoidDict = {}
    for geoidsgeometry in geoids:
      geoidDict[geoidsgeometry[0]] = geoidsgeometry[1]
    return geoidDict

  def GetProcessedGeoIDExtend(self):
    geoidsSQL = "SELECT geoid, geometry FROM block_centroid_intersection_extend"
    result, geoids = self.select_many(geoidsSQL)
    geoidDict = {}
    for geoidsgeometry in geoids:
      geoidDict[geoidsgeometry[0]] = geoidsgeometry[1]
    return geoidDict

  def SetBlockCommute (self, homegeoid, workgeoid, route_length):
    setSQL = "UPDATE origindestination SET o_d_commute = ? WHERE h_geocode = ? and w_geocode = ?"
    # print ("about to execute SQL {} with homegeoid {} and workgeoid {} and length of {}".format(setSQL, homegeoid, workgeoid, route_length))
    self.exec(setSQL, (route_length, homegeoid, workgeoid))

  def SetNearestStreetInfo(self, homegeoid, lat_long_key, distance_to_edge,
                                 osmid, remaining_length):
    setSQL = "INSERT INTO nearest_street_node_info (geoid, lat_long_end, dist_to_edge, " \
             "osmid_edge, length_along_edge) VALUES (?, ?, ?, ?, ?)"
    self.exec(setSQL, (str(homegeoid), str(lat_long_key), distance_to_edge,
                                 osmid, remaining_length))

  def InsertBlockCommute(self, homegeoid, workgeoid, route_length):
    setSQL = "INSERT INTO commute_distances (h_geocode, w_geocode, distance) VALUES (?, ?, ?)"
    self.exec(setSQL, (str(homegeoid), str(workgeoid), route_length))

  def InsertCensusBlock(self, homegeoid, easting, northing, is_commute_block):
    setSQL = "INSERT INTO census_blocks (geocode, easting, northing, is_commute_block) VALUES (?, ?, ?, ?)"
    self.exec(setSQL, (str(homegeoid), easting, northing, int(is_commute_block)))

  def TruncateBlockCommute(self):
    setSQL = "DELETE FROM commute_distances"
    self.exec_s(setSQL)

  def GetMissingBlocks(self):

    sql = "select bc.geoid from street_segment_block_centroid_connectors_extend bc " \
          "left outer join tl_2016_06000_roads_la_clipped_extended tl on bc.geoid = tl.geoid " \
          "where tl.linearid is null"

    result, geoids = self.select_many(sql)
    geoidList = []
    for geoidsgeometry in geoids:
      geoidList.append(geoidsgeometry[0])
    return geoidList

  def GetGTEdgeKey(self, geoid):
    sql = "SELECT lat_long_end FROM nearest_street_node_info " \
          "WHERE geoid = ?"
    return self.select_one(sql, (geoid,))

  def GetAdditionalCommuteLengths(self, geoid):
    sql = "SELECT dist_to_edge + length_along_edge as additional_distance " \
          "FROM nearest_street_node_info " \
          "WHERE geoid = ?"
    return self.select_one(sql, (geoid,))