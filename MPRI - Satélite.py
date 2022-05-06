import processing
import os
from PyQt5.QtCore import *
from qgis.analysis import *
from PyQt5.QtGui import *

layers = iface.mapCanvas().layers()
shapes = []
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
		gustavo = layer.dataProvider().dataSourceUri()

x = 0
num_elementos_shapes = len(shapes)
while(x < num_elementos_shapes):
	vetor = shapes[x]
	ext = extencao[x]
	crs = coordenadas[x]
	(myDirectory,nameFile) = os.path.split(vetor)
	filename = nameFile.rsplit(".",1)[0]
	output = myDirectory + "\\Recortado" + filename + ".tif"
	parametros = {'INPUT': gustavo, 'MASK': vetor, 'NODATA': -1, 'ALPHA_BAND': True, 'CROP_TO_CUTLINE': True, 'KEEP_RESOLUTION': True, 'OPTIONS': "", 'DATA_TYPE': 5, 'OUTPUT': output}
	recortado = processing.run("gdal:cliprasterbymasklayer", parametros)
	iface.addRasterLayer(output, filename)

	raster = QgsRasterLayer(output)
	r = QgsRasterCalculatorEntry()
	g = QgsRasterCalculatorEntry()
	b = QgsRasterCalculatorEntry()
	r.raster = raster
	g.raster = raster
	b.raster = raster
	r.bandNumber = 1
	g.bandNumber = 2
	b.bandNumber = 3
	r.ref = 'raster@1'
	g.ref = 'raster@2'
	b.ref = 'raster@3'

	referenciasmpri = (g.ref, r.ref, g.ref, r.ref)
	exp = "(%s - %s) / (%s + %s)" % referenciasmpri
	mpri_saida = myDirectory + "\\MPRI" + nameFile + ".tif"
	e = raster.extent()
	w = raster.width()
	h = raster.height()
	entries = [g, r]
	mpri = QgsRasterCalculator(exp, mpri_saida, "GTiff", e, w, h, entries)
	mpri.processCalculation()
	nomempri = nameFile + "MPRI"
	rlayer = iface.addRasterLayer(mpri_saida, nomempri)
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

	parametros1 = {'TYPE': 2, 'EXTENT': ext, 'HSPACING': 5.0, 'VSPACING': 5.0, 'HOVERLAY': 0.0, 'VOVERLAY': 0.0, 'CRS': crs, 'OUTPUT': 'TEMPORARY_OUTPUT'}
	gridado = processing.run("qgis:creategrid", parametros1)
	saidagridado = gridado['OUTPUT']
	saidaclipado = myDirectory + "\\MPRI_Zona de manejo" + nameFile + ".shp"
	parametros2 = {'INPUT': saidagridado, 'OVERLAY': vetor, 'OUTPUT': saidaclipado}
	clipado = processing.run("qgis:clip", parametros2)
	zonampri = iface.addVectorLayer(saidaclipado, 'Zona de Manejo', 'ogr')

	media = [2]
	parametrosm = {'INPUT_RASTER': mpri_saida, 'RASTER_BAND': 1, 'INPUT_VECTOR': saidaclipado, 'COLUMN_PREFIX': 'MPRI', 'STATS': media}
	saida = processing.run("qgis:zonalstatistics", parametrosm)
	ramp_name = 'NDVI'
	value_field = 'MPRImean'
	num_classes = 5
	classification_method = QgsClassificationJenks()
	layer = zonampri
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