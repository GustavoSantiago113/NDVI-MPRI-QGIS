#Autor: Gustavo Nocera Santiago

import processing
import os
from osgeo import gdal, ogr
from PyQt5.QtCore import *
from qgis.analysis import *
from PyQt5.QtGui import *
from pathlib import Path
import jenkspy

gdal.UseExceptions()

layers = iface.mapCanvas().layers()
shapes = []
rastersRGB = []
rastersMULTI = []
extencao = []
coordenadas = []

for layer in layers:
	layerType = layer.type()
	if layerType == QgsMapLayer.VectorLayer:
		myfilepath = layer.dataProvider().dataSourceUri()
		shapes.append(myfilepath)
		xmin = (layer.extent().xMinimum()) 
		xmax = (layer.extent().xMaximum()) 
		ymin = (layer.extent().yMinimum()) 
		ymax = (layer.extent().yMaximum()) 
		extent = str(xmin)+ ',' + str(xmax)+ ',' +str(ymin)+ ',' +str(ymax)
		extencao.append(extent)
		coordenada = layer.crs().authid()
		coordenadas.append(coordenada)
	if layerType == QgsMapLayer.RasterLayer:
		g = layer.bandCount()
		if g > 4:
			gustavo = layer.dataProvider().dataSourceUri()
			rastersMULTI.append(gustavo)

		if g == 4:
			gustavoRGB = layer.dataProvider().dataSourceUri()
			rastersRGB.append(gustavoRGB)

NDVI = []
w = 0
num_elementos_rastersMULTI = len(rastersMULTI)
while(w < num_elementos_rastersMULTI):
	
	NDVIc = rastersMULTI[w]
	(myDirectory,nameFile) = os.path.split(NDVIc)
	filename = nameFile.rsplit(".",1)[0]
	raster = QgsRasterLayer(NDVIc)
	ir = QgsRasterCalculatorEntry()
	r = QgsRasterCalculatorEntry()
	g = QgsRasterCalculatorEntry()
	re = QgsRasterCalculatorEntry()
	ir.raster = raster
	r.raster = raster
	g.raster = raster
	re.raster = raster
	ir.bandNumber = 4
	r.bandNumber = 2
	g.bandNumber = 1
	re.bandNumber = 3
	ir.ref = 'raster@4'
	r.ref = 'raster@2'
	g.ref = 'raster@1'
	re.ref = 'raster@3'

	referenciasndvi = (ir.ref, r.ref, ir.ref, r.ref)
	exp = "(%s - %s) / (%s + %s)" % referenciasndvi
	ndvi_saida = myDirectory + "\\NDVI " + filename + ".tif"
	nomesaida = "NDVI " + filename
	e = raster.extent()
	w = raster.width()
	h = raster.height()
	entries = [ir,r]
	ndvi = QgsRasterCalculator(exp, ndvi_saida, "GTiff", e, w, h, entries)
	ndvi.processCalculation()
	rlayer = iface.addRasterLayer(ndvi_saida, nomesaida)
	NDVI.append(ndvi_saida)

	stats = rlayer.dataProvider().bandStatistics(1, QgsRasterBandStats.All)
	min = stats.minimumValue
	max = stats.maximumValue
	interval1 = (min + ((max-min)/4))
	interval2 = (min + ((max-min)/2))
	interval3 = (min + 3*((max-min)/4))
	fnc = QgsColorRampShader()
	fnc.setColorRampType(QgsColorRampShader.Interpolated)
	lst = (QgsColorRampShader.ColorRampItem(min, QColor(215, 25, 28), 'Nenhuma Vegetação'), \
	QgsColorRampShader.ColorRampItem(interval1, QColor(253, 174, 97), 'Pouca Vegetação'), \
	QgsColorRampShader.ColorRampItem(interval2, QColor(255, 255, 192), 'Média Vegetação'), \
	QgsColorRampShader.ColorRampItem(interval3, QColor(166, 217, 106), 'Moderada Vegetação'), \
	QgsColorRampShader.ColorRampItem(max, QColor(26, 150, 65), 'Muita Vegetação'))
	fnc.setColorRampItemList(lst)
	shader = QgsRasterShader()
	shader.setRasterShaderFunction(fnc)
	renderer = QgsSingleBandPseudoColorRenderer(rlayer.dataProvider(), 1, shader)
	rlayer.setRenderer(renderer)
	w += 1


num_elementos_shapes = len(shapes)
x = 0

while(x < num_elementos_shapes):

	vetor = shapes[x]
	ext = extencao[x]
	crs = coordenadas[x]
	for rasterRGB in rastersRGB:
		(myDirectory,nameFile) = os.path.split(vetor)
		(myDirectory1,nameFile1) = os.path.split(rasterRGB)
		filename = nameFile.rsplit(".",1)[0]
		filename1 = nameFile1.rsplit(".",1)[0]
		nomesaidaRGB = filename1 + " " + filename
		output = myDirectory + "\\ " + filename1+ " " + filename + ".tif"
		result = gdal.Warp(output, rasterRGB, cutlineDSName=vetor, cropToCutline = True)
		saida = iface.addRasterLayer(output, nomesaidaRGB)

	for rastersNDVI in NDVI:
		(myDirectory,nameFile) = os.path.split(vetor)
		filename = nameFile.rsplit(".",1)[0]
		nomesaidaNDVI = "NDVI " + filename
		output = myDirectory + "\\NDVI  " + filename + ".tif"
		result = gdal.Warp(output, rastersNDVI, cutlineDSName=vetor, cropToCutline = True)
		ndvirecortado = iface.addRasterLayer(output, nomesaidaNDVI)

		stats = ndvirecortado.dataProvider().bandStatistics(1, QgsRasterBandStats.All)
		min = stats.minimumValue
		max = stats.maximumValue
		interval1 = (min + ((max-min)/4))
		interval2 = (min + ((max-min)/2))
		interval3 = (min + 3*((max-min)/4))
		fnc = QgsColorRampShader()
		fnc.setColorRampType(QgsColorRampShader.Interpolated)
		lst = (QgsColorRampShader.ColorRampItem(min, QColor(215, 25, 28), 'Nenhuma Vegetação'), \
		QgsColorRampShader.ColorRampItem(interval1, QColor(253, 174, 97), 'Pouca Vegetação'), \
		QgsColorRampShader.ColorRampItem(interval2, QColor(255, 255, 192), 'Média Vegetação'), \
		QgsColorRampShader.ColorRampItem(interval3, QColor(166, 217, 106), 'Moderada Vegetação'), \
		QgsColorRampShader.ColorRampItem(max, QColor(26, 150, 65), 'Muita Vegetação'))
		fnc.setColorRampItemList(lst)
		shader = QgsRasterShader()
		shader.setRasterShaderFunction(fnc)
		renderer = QgsSingleBandPseudoColorRenderer(ndvirecortado.dataProvider(), 1, shader)
		ndvirecortado.setRenderer(renderer)
		
		parametros1 = {'TYPE': 2, 'EXTENT': ext, 'HSPACING': 5.0, 'VSPACING': 5.0, 'HOVERLAY': 0.0, 'VOVERLAY': 0.0, 'CRS': crs, 'OUTPUT': 'TEMPORARY_OUTPUT'}
		gridado = processing.run("qgis:creategrid", parametros1)
		saidagridado = gridado['OUTPUT']
		saidaclipado = myDirectory + "\\Zona de manejo NDVI  " + filename + ".shp"
		nomesaidazona = "Zona NDVI " + filename
		parametros2 = {'INPUT': saidagridado, 'OVERLAY': vetor, 'OUTPUT': saidaclipado}
		clipado = processing.run("qgis:clip", parametros2)
		zonandvi = iface.addVectorLayer(saidaclipado, nomesaidazona, 'ogr')
		media = [2]
		parametrosm = {'INPUT_RASTER': output, 'RASTER_BAND': 1, 'INPUT_VECTOR': saidaclipado, 'COLUMN_PREFIX': 'NDVI', 'STATS': media}
		saida = processing.run("qgis:zonalstatistics", parametrosm)
		
		caps = zonandvi.dataProvider().capabilities()

		NDVIv = []
		zonandvi.updateFields()
		idnull = []
		with edit(zonandvi):
			for f in zonandvi.getFeatures():
				if f['NDVImean'] == qgis.core.NULL:
					idnull.append(f.id())
				if f['NDVImean'] != qgis.core.NULL:
					pass
		if caps & QgsVectorDataProvider.DeleteFeatures:
			res = zonandvi.dataProvider().deleteFeatures(idnull)
		with edit(zonandvi):
			for f in zonandvi.getFeatures():
				ndviv = f['NDVImean']
				NDVIv.append(ndviv)

		JENKS = []
		JENKS = jenkspy.jenks_breaks(NDVIv, nb_class=5)

		jenks = JENKS[0]
		jenks = str(jenks)
		jenks1 = JENKS[1]
		jenks1 = str(jenks1)
		jenks2 = JENKS[2]
		jenks2 = str(jenks2)
		jenks3 = JENKS[3]
		jenks3 = str(jenks3)
		jenks4 = JENKS[4]
		jenks4 = str(jenks4)
		jenks5 = JENKS[5]
		jenks5 = str(jenks5)

		dissolvidos = []
		zonandvi.selectByExpression('"NDVImean">'+jenks+' and "NDVImean"<'+jenks1+'', QgsVectorLayer.SetSelection)
		dissolved = processing.run("qgis:dissolve", {'INPUT': QgsProcessingFeatureSourceDefinition(saidaclipado, selectedFeaturesOnly=True, featureLimit=-1, 		geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid), 'OUTPUT': 'TEMPORARY_OUTPUT'})
		saida = dissolved['OUTPUT']
		dissolvidos.append(saida)
		zonandvi.removeSelection()

		zonandvi.selectByExpression('"NDVImean">'+jenks1+' and "NDVImean"<'+jenks2+'', QgsVectorLayer.SetSelection)
		dissolved = processing.run("qgis:dissolve", {'INPUT': QgsProcessingFeatureSourceDefinition(saidaclipado, selectedFeaturesOnly=True, featureLimit=-1, 		geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid), 'OUTPUT': 'TEMPORARY_OUTPUT'})
		saida = dissolved['OUTPUT']
		dissolvidos.append(saida)
		zonandvi.removeSelection()

		zonandvi.selectByExpression('"NDVImean">'+jenks2+' and "NDVImean"<'+jenks3+'', QgsVectorLayer.SetSelection)
		dissolved = processing.run("qgis:dissolve", {'INPUT': QgsProcessingFeatureSourceDefinition(saidaclipado, selectedFeaturesOnly=True, featureLimit=-1, 		geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid), 'OUTPUT': 'TEMPORARY_OUTPUT'})
		saida = dissolved['OUTPUT']
		dissolvidos.append(saida)
		zonandvi.removeSelection()

		zonandvi.selectByExpression('"NDVImean">'+jenks3+' and "NDVImean"<'+jenks4+'', QgsVectorLayer.SetSelection)
		dissolved = processing.run("qgis:dissolve", {'INPUT': QgsProcessingFeatureSourceDefinition(saidaclipado, selectedFeaturesOnly=True, featureLimit=-1, 		geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid), 'OUTPUT': 'TEMPORARY_OUTPUT'})
		saida = dissolved['OUTPUT']
		dissolvidos.append(saida)
		zonandvi.removeSelection()

		zonandvi.selectByExpression('"NDVImean">'+jenks4+' and "NDVImean"<'+jenks5+'', QgsVectorLayer.SetSelection)
		dissolved = processing.run("qgis:dissolve", {'INPUT': QgsProcessingFeatureSourceDefinition(saidaclipado, selectedFeaturesOnly=True, featureLimit=-1, 		geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid), 'OUTPUT': 'TEMPORARY_OUTPUT'})
		saida = dissolved['OUTPUT']
		dissolvidos.append(saida)
		zonandvi.removeSelection()

		nomesaidamesclado = filename + " mesclado"
		saidamesclado = myDirectory + "\\ Zona NDVI" + filename + " mesclado.shp"
		mesclado = processing.run("qgis:mergevectorlayers", {'LAYERS': dissolvidos,  'OUTPUT': saidamesclado})
		zonandvimesclado = iface.addVectorLayer(saidamesclado, nomesaidamesclado, 'ogr')	
		
		NDVIv = []
		JENKS = []
		idnull = []
		dissolvidos = []
		QgsProject.instance().removeMapLayer(zonandvi.id())

		features = zonandvimesclado.getFeatures()
		caps = zonandvimesclado.dataProvider().capabilities()
		dfeats = []
		if caps & QgsVectorDataProvider.AddAttributes:
			res = zonandvimesclado.dataProvider().addAttributes([QgsField('Area', QVariant.Double)])
			zonandvimesclado.updateFields()

		expression = QgsExpression('$area / 10000')

		context = QgsExpressionContext()
		context.appendScopes(\
		QgsExpressionContextUtils.globalProjectLayerScopes(zonandvimesclado))

		with edit(zonandvimesclado):
			for f in zonandvimesclado.getFeatures():
				context.setFeature(f)
				f['Area'] = expression.evaluate(context)
				zonandvimesclado.updateFeature(f)

		ramp_name = 'Prisma'
		value_field = 'NDVImean'
		num_classes = 5
		classification_method = QgsClassificationJenks()
		layer = zonandvimesclado
		format = QgsRendererRangeLabelFormat()
		format.setFormat("%1 - %2")
		format.setPrecision(2)
		format.setTrimTrailingZeroes(True)
		default_style = QgsStyle().defaultStyle()
		color_ramp = default_style.colorRamp(ramp_name)
		renderer = QgsGraduatedSymbolRenderer()
		renderer.setClassAttribute(value_field)
		renderer.setClassificationMethod(classification_method)
		renderer.setLabelFormat(format)
		renderer.updateClasses(layer, num_classes)
		renderer.updateColorRamp(color_ramp)
		layer.setRenderer(renderer)
		layer.triggerRepaint()

	x+=1
